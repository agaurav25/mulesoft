%dw 2.0
output application/json
import * from dw::core::Arrays
import * from dw::core::Objects
import * from dw::core::Strings
import * from dw::core::Dates

// Input variables
var orders = payload.orders
var products = vars.productCatalog default {}
var customers = vars.customerData default {}
var analyticsConfig = vars.analyticsConfig default {
    includeTimeSeriesAnalysis: true,
    includeCustomerSegmentation: true,
    includeProductPerformance: true,
    includePredictiveMetrics: false,
    timeRangeInDays: 30
}

// Date and time utility functions
fun parseOrderDate(dateString: String): Date = 
    dateString as Date {format: "yyyy-MM-dd"}

fun getDateRange(orders: Array): Object = {
    startDate: min(orders map parseOrderDate($.orderDate)),
    endDate: max(orders map parseOrderDate($.orderDate)),
    totalDays: (max(orders map parseOrderDate($.orderDate)) - min(orders map parseOrderDate($.orderDate))) / |P1D| as Number
}

fun filterOrdersByDateRange(orders: Array, days: Number): Array = 
    orders filter (parseOrderDate($.orderDate) >= (now() - |P$(days)D|))

fun groupOrdersByPeriod(orders: Array, period: String): Object = 
    orders groupBy (order) -> 
        parseOrderDate(order.orderDate) match {
            case date if (period == "daily") -> date as String {format: "yyyy-MM-dd"}
            case date if (period == "weekly") -> date as String {format: "yyyy-'W'ww"}
            case date if (period == "monthly") -> date as String {format: "yyyy-MM"}
            case date if (period == "quarterly") -> date as String {format: "yyyy-'Q'Q"}
            else -> date as String {format: "yyyy-MM-dd"}
        }

// Customer analysis functions
fun analyzeCustomerBehavior(orders: Array): Object = {
    var customerOrders = orders groupBy $.customerId
    
    customerOrders mapObject (customerOrderList, customerId) -> {
        (customerId): {
            totalOrders: sizeOf(customerOrderList),
            totalSpent: sum(customerOrderList map $.totalAmount),
            averageOrderValue: avg(customerOrderList map $.totalAmount),
            firstOrderDate: min(customerOrderList map parseOrderDate($.orderDate)),
            lastOrderDate: max(customerOrderList map parseOrderDate($.orderDate)),
            daysBetweenFirstAndLast: if (sizeOf(customerOrderList) > 1) 
                (max(customerOrderList map parseOrderDate($.orderDate)) - min(customerOrderList map parseOrderDate($.orderDate))) / |P1D| as Number
            else 0,
            averageDaysBetweenOrders: if (sizeOf(customerOrderList) > 1)
                ((max(customerOrderList map parseOrderDate($.orderDate)) - min(customerOrderList map parseOrderDate($.orderDate))) / |P1D| as Number) / (sizeOf(customerOrderList) - 1)
            else null,
            orderFrequency: categorizeOrderFrequency(customerOrderList),
            preferredCategories: analyzeCustomerPreferences(customerOrderList),
            lifetimeValue: calculateCustomerLifetimeValue(customerOrderList),
            riskScore: calculateCustomerRiskScore(customerOrderList)
        }
    }
}

fun categorizeOrderFrequency(customerOrders: Array): String = 
    if (sizeOf(customerOrders) == 1) "ONE_TIME"
    else {
        var avgDaysBetween = ((max(customerOrders map parseOrderDate($.orderDate)) - min(customerOrders map parseOrderDate($.orderDate))) / |P1D| as Number) / (sizeOf(customerOrders) - 1)
        avgDaysBetween match {
            case days if (days <= 7) -> "WEEKLY"
            case days if (days <= 30) -> "MONTHLY"
            case days if (days <= 90) -> "QUARTERLY"
            else -> "OCCASIONAL"
        }
    }

fun analyzeCustomerPreferences(customerOrders: Array): Array = 
    flatten(customerOrders map $.items)
        map $.category
        groupBy ($)
        mapObject (items, category) -> {
            category: category,
            frequency: sizeOf(items),
            totalSpent: sum(customerOrders 
                map $.items 
                filter ($.category == category) 
                map ($.quantity * $.unitPrice))
        }
        pluck ($)
        orderBy (-$.frequency)
        take 5

fun calculateCustomerLifetimeValue(customerOrders: Array): Number = {
    var totalSpent = sum(customerOrders map $.totalAmount)
    var orderCount = sizeOf(customerOrders)
    var avgOrderValue = totalSpent / orderCount
    var orderFrequencyPerYear = if (orderCount > 1) {
        var daysBetweenFirstAndLast = (max(customerOrders map parseOrderDate($.orderDate)) - min(customerOrders map parseOrderDate($.orderDate))) / |P1D| as Number
        if (daysBetweenFirstAndLast > 0) (orderCount - 1) * 365 / daysBetweenFirstAndLast else orderCount
    } else 1
    
    // Simple CLV calculation: avg order value * frequency * estimated lifespan (2 years)
    avgOrderValue * orderFrequencyPerYear * 2
}

fun calculateCustomerRiskScore(customerOrders: Array): Number = {
    var daysSinceLastOrder = (now() - max(customerOrders map parseOrderDate($.orderDate))) / |P1D| as Number
    var orderConsistency = if (sizeOf(customerOrders) > 1) {
        var avgTimeBetween = ((max(customerOrders map parseOrderDate($.orderDate)) - min(customerOrders map parseOrderDate($.orderDate))) / |P1D| as Number) / (sizeOf(customerOrders) - 1)
        if (daysSinceLastOrder > avgTimeBetween * 2) 50 else 10
    } else if (daysSinceLastOrder > 90) 75 else 25
    
    var spendingTrend = analyzeSpendingTrend(customerOrders)
    
    orderConsistency + spendingTrend
}

fun analyzeSpendingTrend(customerOrders: Array): Number = 
    if (sizeOf(customerOrders) >= 3) {
        var sortedOrders = customerOrders orderBy parseOrderDate($.orderDate)
        var recentOrders = sortedOrders[-3 to -1]
        var olderOrders = sortedOrders[0 to 2]
        var recentAvg = avg(recentOrders map $.totalAmount)
        var olderAvg = avg(olderOrders map $.totalAmount)
        
        if (recentAvg < olderAvg * 0.7) 30  // Decreasing spend
        else if (recentAvg > olderAvg * 1.3) -10  // Increasing spend
        else 0  // Stable spend
    } else 0

// Product analysis functions
fun analyzeProductPerformance(orders: Array): Object = {
    var allItems = flatten(orders map $.items)
    var productSales = allItems groupBy $.productId
    
    productSales mapObject (productItems, productId) -> {
        (productId): {
            totalQuantitySold: sum(productItems map $.quantity),
            totalRevenue: sum(productItems map ($.quantity * $.unitPrice)),
            averagePrice: avg(productItems map $.unitPrice),
            uniqueCustomers: sizeOf(distinct(orders filter (order) -> 
                (order.items map $.productId) contains productId) map $.customerId),
            salesFrequency: sizeOf(productItems),
            category: productItems[0].category,
            performanceRank: null, // Will be calculated after all products are processed
            inventoryTurnover: calculateInventoryTurnover(productItems),
            seasonalTrends: analyzeSeasonalTrends(orders, productId)
        }
    }
}

fun calculateInventoryTurnover(productItems: Array): Number = {
    var totalSold = sum(productItems map $.quantity)
    var averageInventory = 100 // Placeholder - would come from inventory system
    totalSold / averageInventory
}

fun analyzeSeasonalTrends(orders: Array, productId: String): Object = {
    var productOrders = orders filter (order) -> 
        (order.items map $.productId) contains productId
    
    var monthlyData = productOrders groupBy (order) -> 
        parseOrderDate(order.orderDate) as String {format: "MM"}
    
    monthlyData mapObject (monthOrders, month) -> {
        (month): {
            orderCount: sizeOf(monthOrders),
            revenue: sum(flatten(monthOrders map $.items) 
                filter ($.productId == productId) 
                map ($.quantity * $.unitPrice))
        }
    }
}

// Time series analysis functions
fun performTimeSeriesAnalysis(orders: Array): Object = {
    var dailyData = groupOrdersByPeriod(orders, "daily")
    var weeklyData = groupOrdersByPeriod(orders, "weekly")
    var monthlyData = groupOrdersByPeriod(orders, "monthly")
    
    {
        daily: analyzePeriodData(dailyData),
        weekly: analyzePeriodData(weeklyData),
        monthly: analyzePeriodData(monthlyData),
        trends: {
            salesGrowth: calculateGrowthRate(monthlyData),
            seasonality: detectSeasonality(monthlyData),
            volatility: calculateVolatility(dailyData)
        }
    }
}

fun analyzePeriodData(periodData: Object): Object = 
    periodData mapObject (periodOrders, period) -> {
        (period): {
            orderCount: sizeOf(periodOrders),
            totalRevenue: sum(periodOrders map $.totalAmount),
            averageOrderValue: avg(periodOrders map $.totalAmount),
            uniqueCustomers: sizeOf(distinct(periodOrders map $.customerId))
        }
    }

fun calculateGrowthRate(monthlyData: Object): Number = {
    var sortedMonths = monthlyData pluck $ orderBy $.period
    if (sizeOf(sortedMonths) >= 2) {
        var currentMonth = sortedMonths[-1]
        var previousMonth = sortedMonths[-2]
        var currentRevenue = sum(currentMonth map $.totalAmount)
        var previousRevenue = sum(previousMonth map $.totalAmount)
        
        if (previousRevenue > 0) 
            ((currentRevenue - previousRevenue) / previousRevenue) * 100
        else 0
    } else 0
}

fun detectSeasonality(monthlyData: Object): Object = {
    var monthlyRevenues = monthlyData mapObject (monthOrders, month) -> {
        (month): sum(monthOrders map $.totalAmount)
    }
    
    var avgRevenue = avg(monthlyRevenues pluck $)
    var maxMonth = monthlyRevenues maxBy ($)
    var minMonth = monthlyRevenues minBy ($)
    
    {
        isSeasonsal: (maxMonth - minMonth) / avgRevenue > 0.3,
        peakMonth: monthlyRevenues filterObject ((revenue, month) -> revenue == maxMonth) pluck $$ as Array,
        lowMonth: monthlyRevenues filterObject ((revenue, month) -> revenue == minMonth) pluck $$ as Array,
        seasonalityIndex: (maxMonth - minMonth) / avgRevenue
    }
}

fun calculateVolatility(dailyData: Object): Number = {
    var dailyRevenues = dailyData pluck (sum($ map $.totalAmount))
    var avgRevenue = avg(dailyRevenues)
    var variance = avg(dailyRevenues map (pow($ - avgRevenue, 2)))
    sqrt(variance)
}

// Predictive analytics functions
fun generatePredictiveMetrics(orders: Array): Object = {
    var customerBehavior = analyzeCustomerBehavior(orders)
    var recentTrends = performTimeSeriesAnalysis(filterOrdersByDateRange(orders, 30))
    
    {
        churnPrediction: predictCustomerChurn(customerBehavior),
        revenueForecasting: forecastRevenue(recentTrends),
        inventoryRecommendations: generateInventoryRecommendations(orders),
        marketingInsights: generateMarketingInsights(customerBehavior, orders)
    }
}

fun predictCustomerChurn(customerBehavior: Object): Object = {
    var churnRisks = customerBehavior mapObject (behavior, customerId) -> {
        (customerId): {
            riskScore: behavior.riskScore,
            churnProbability: if (behavior.riskScore > 70) "HIGH"
                else if (behavior.riskScore > 40) "MEDIUM"
                else "LOW",
            daysSinceLastOrder: (now() - behavior.lastOrderDate) / |P1D| as Number,
            recommendedAction: if (behavior.riskScore > 70) "IMMEDIATE_OUTREACH"
                else if (behavior.riskScore > 40) "PROMOTIONAL_CAMPAIGN"
                else "MAINTAIN_ENGAGEMENT"
        }
    }
    
    {
        highRiskCustomers: churnRisks filterObject ((risk, customerId) -> risk.churnProbability == "HIGH") pluck $$,
        totalHighRisk: sizeOf(churnRisks filterObject ((risk, customerId) -> risk.churnProbability == "HIGH")),
        totalMediumRisk: sizeOf(churnRisks filterObject ((risk, customerId) -> risk.churnProbability == "MEDIUM")),
        totalLowRisk: sizeOf(churnRisks filterObject ((risk, customerId) -> risk.churnProbability == "LOW")),
        recommendedActions: churnRisks groupBy $.recommendedAction mapObject (actions, actionType) -> {
            (actionType): sizeOf(actions)
        }
    }
}

fun forecastRevenue(recentTrends: Object): Object = {
    var monthlyRevenues = recentTrends.monthly pluck (sum($ map $.totalRevenue))
    var avgMonthlyGrowth = if (sizeOf(monthlyRevenues) >= 2) {
        var growthRates = monthlyRevenues[1 to -1] map (item, index) -> 
            if (monthlyRevenues[index] > 0) ((item - monthlyRevenues[index]) / monthlyRevenues[index]) * 100 else 0
        avg(growthRates)
    } else 0
    
    var lastMonthRevenue = monthlyRevenues[-1]
    
    {
        nextMonthForecast: lastMonthRevenue * (1 + avgMonthlyGrowth / 100),
        nextQuarterForecast: lastMonthRevenue * 3 * (1 + avgMonthlyGrowth / 100),
        confidenceLevel: if (abs(avgMonthlyGrowth) < 10) "HIGH" else if (abs(avgMonthlyGrowth) < 25) "MEDIUM" else "LOW",
        growthRate: avgMonthlyGrowth
    }
}

fun generateInventoryRecommendations(orders: Array): Array = {
    var productPerformance = analyzeProductPerformance(orders)
    var recentOrders = filterOrdersByDateRange(orders, 30)
    var recentProductSales = flatten(recentOrders map $.items) groupBy $.productId
    
    productPerformance pluck ((performance, productId) -> {
        productId: productId,
        category: performance.category,
        recommendation: if (performance.totalQuantitySold > 100) "INCREASE_STOCK"
            else if (performance.totalQuantitySold < 10) "REDUCE_STOCK"
            else "MAINTAIN_CURRENT",
        urgency: if (recentProductSales[productId] != null and sizeOf(recentProductSales[productId]) > 20) "HIGH"
            else if (recentProductSales[productId] != null and sizeOf(recentProductSales[productId]) > 5) "MEDIUM"
            else "LOW",
        suggestedQuantity: calculateSuggestedQuantity(performance, recentProductSales[productId] default [])
    }) orderBy (-$.urgency == "HIGH")
}

fun calculateSuggestedQuantity(performance: Object, recentSales: Array): Number = {
    var avgMonthlySales = performance.totalQuantitySold / 3 // Assuming 3 months of data
    var safetyStock = avgMonthlySales * 0.2 // 20% safety stock
    var reorderPoint = avgMonthlySales + safetyStock
    
    round(reorderPoint)
}

fun generateMarketingInsights(customerBehavior: Object, orders: Array): Object = {
    var customerSegments = customerBehavior groupBy $.orderFrequency
    var topSpenders = customerBehavior pluck $ orderBy (-$.totalSpent) take 10
    var categoryPerformance = flatten(orders map $.items) groupBy $.category
    
    {
        customerSegments: customerSegments mapObject (customers, segment) -> {
            (segment): {
                count: sizeOf(customers),
                averageLifetimeValue: avg(customers map $.lifetimeValue),
                recommendedStrategy: segment match {
                    case "WEEKLY" -> "LOYALTY_PROGRAM"
                    case "MONTHLY" -> "SUBSCRIPTION_MODEL"
                    case "QUARTERLY" -> "SEASONAL_CAMPAIGNS"
                    case "OCCASIONAL" -> "WIN_BACK_CAMPAIGNS"
                    else -> "ACTIVATION_CAMPAIGNS"
                }
            }
        },
        topCustomers: topSpenders map {
            customerId: $.customerId,
            lifetimeValue: $.lifetimeValue,
            orderFrequency: $.orderFrequency,
            recommendedTreatment: if ($.lifetimeValue > 10000) "VIP_TREATMENT"
                else if ($.lifetimeValue > 5000) "PREMIUM_SUPPORT"
                else "STANDARD_CARE"
        },
        categoryInsights: categoryPerformance mapObject (items, category) -> {
            (category): {
                totalItems: sizeOf(items),
                totalRevenue: sum(items map ($.quantity * $.unitPrice)),
                marketShare: (sizeOf(items) / sizeOf(flatten(orders map $.items))) * 100,
                growthPotential: if (sizeOf(items) > 100) "MATURE" else "GROWTH"
            }
        }
    }
}

// Main transformation
---
{
    // Executive Summary
    summary: {
        totalOrders: sizeOf(orders),
        totalRevenue: sum(orders map $.totalAmount),
        averageOrderValue: avg(orders map $.totalAmount),
        uniqueCustomers: sizeOf(distinct(orders map $.customerId)),
        dateRange: getDateRange(orders),
        analysisTimestamp: now()
    },
    
    // Customer Analytics
    customerAnalytics: if (analyticsConfig.includeCustomerSegmentation) 
        analyzeCustomerBehavior(orders) 
    else null,
    
    // Product Performance
    productPerformance: if (analyticsConfig.includeProductPerformance) 
        analyzeProductPerformance(orders) 
    else null,
    
    // Time Series Analysis
    timeSeriesAnalysis: if (analyticsConfig.includeTimeSeriesAnalysis) 
        performTimeSeriesAnalysis(filterOrdersByDateRange(orders, analyticsConfig.timeRangeInDays)) 
    else null,
    
    // Predictive Metrics
    predictiveAnalytics: if (analyticsConfig.includePredictiveMetrics) 
        generatePredictiveMetrics(orders) 
    else null,
    
    // Configuration and Metadata
    metadata: {
        configurationUsed: analyticsConfig,
        dataQuality: {
            completeness: (sizeOf(orders filter ($.customerId != null and $.totalAmount != null)) / sizeOf(orders)) * 100,
            timeSpan: getDateRange(orders),
            recordsProcessed: sizeOf(orders)
        },
        processingInfo: {
            processingTime: (now() - vars.startTime) as Number default 0,
            memoryUsage: sizeOf(write(orders, "application/json")) / 1024, // Approximate KB
            transformationVersion: "3.0.0"
        }
    }
}