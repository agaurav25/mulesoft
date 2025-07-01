%dw 2.0
output application/json
import * from dw::core::Arrays
import * from dw::core::Objects
import * from dw::core::Strings
import formatDateTime from dw::core::Dates

// Input variables
var customers = payload.customers
var enrichmentData = vars.enrichmentData default {}
var transformationConfig = vars.transformationConfig default {
    includeMetadata: true,
    formatPhoneNumbers: true,
    calculateAge: true,
    includePreferences: false
}

// Utility functions for customer data transformation
fun formatPhoneNumber(phone: String): String = 
    phone replace /[^\d]/ with "" match {
        case phoneDigits if (sizeOf(phoneDigits) == 10) -> 
            "(" ++ phoneDigits[0 to 2] ++ ") " ++ phoneDigits[3 to 5] ++ "-" ++ phoneDigits[6 to 9]
        case phoneDigits if (sizeOf(phoneDigits) == 11 and phoneDigits startsWith "1") ->
            "+1 (" ++ phoneDigits[1 to 3] ++ ") " ++ phoneDigits[4 to 6] ++ "-" ++ phoneDigits[7 to 10]
        else -> phone
    }

fun calculateAge(birthDate: Date): Number = 
    (now() - birthDate) / |P365D| as Number {format: "0"}

fun normalizeAddress(address: Object): Object = {
    street: upper(address.street default ""),
    city: capitalize(address.city default ""),
    state: upper(address.state default ""),
    postalCode: address.postalCode default "",
    country: upper(address.country default "US")
}

fun determineCustomerTier(customer: Object): String = 
    customer.totalSpent match {
        case amount if (amount >= 10000) -> "PLATINUM"
        case amount if (amount >= 5000) -> "GOLD"
        case amount if (amount >= 1000) -> "SILVER"
        else -> "BRONZE"
    }

fun getCustomerPreferences(customerId: String): Object = 
    enrichmentData.preferences[customerId] default {
        emailNotifications: true,
        smsNotifications: false,
        marketingOptIn: false,
        language: "en",
        timezone: "America/New_York"
    }

fun enrichWithOrderHistory(customer: Object): Object = 
    customer ++ {
        orderHistory: enrichmentData.orders[customer.customerId as String] default [],
        lastOrderDate: enrichmentData.orders[customer.customerId as String][-1].orderDate default null,
        averageOrderValue: if (!isEmpty(enrichmentData.orders[customer.customerId as String]))
            avg(enrichmentData.orders[customer.customerId as String] map $.totalAmount)
        else 0,
        totalOrders: sizeOf(enrichmentData.orders[customer.customerId as String] default [])
    }

fun validateCustomerData(customer: Object): Object = {
    isValid: customer.email != null and 
             customer.firstName != null and 
             customer.lastName != null and
             customer.email matches /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
    validationErrors: flatten([
        if (customer.email == null) ["Email is required"] else [],
        if (customer.firstName == null) ["First name is required"] else [],
        if (customer.lastName == null) ["Last name is required"] else [],
        if (customer.email != null and !(customer.email matches /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/)) 
            ["Invalid email format"] else []
    ])
}

fun applyBusinessRules(customer: Object): Object = 
    customer ++ {
        canPlaceOrder: customer.status == "ACTIVE" and customer.creditLimit > customer.currentBalance,
        requiresApproval: customer.totalSpent > 50000 or customer.riskScore > 75,
        eligibleForDiscount: customer.loyaltyPoints > 1000 and customer.tier in ["GOLD", "PLATINUM"],
        recommendedProducts: if (customer.lastPurchaseCategory != null)
            enrichmentData.recommendations[customer.lastPurchaseCategory] default []
        else []
    }

fun formatCustomerOutput(customer: Object): Object = {
    // Core customer information
    customerId: customer.customerId,
    personalInfo: {
        firstName: capitalize(customer.firstName),
        lastName: capitalize(customer.lastName),
        fullName: capitalize(customer.firstName) ++ " " ++ capitalize(customer.lastName),
        email: lower(customer.email),
        phone: if (transformationConfig.formatPhoneNumbers) 
            formatPhoneNumber(customer.phone default "") 
        else customer.phone,
        dateOfBirth: customer.dateOfBirth,
        age: if (transformationConfig.calculateAge and customer.dateOfBirth != null) 
            calculateAge(customer.dateOfBirth as Date) 
        else null
    },
    
    // Address information
    address: normalizeAddress(customer.address default {}),
    
    // Account status and tier information
    accountInfo: {
        status: customer.status,
        registrationDate: customer.registrationDate,
        lastLoginDate: customer.lastLoginDate,
        tier: determineCustomerTier(customer),
        loyaltyPoints: customer.loyaltyPoints default 0,
        creditLimit: customer.creditLimit default 0,
        currentBalance: customer.currentBalance default 0,
        availableCredit: (customer.creditLimit default 0) - (customer.currentBalance default 0)
    },
    
    // Financial and spending information
    spendingProfile: {
        totalSpent: customer.totalSpent default 0,
        averageOrderValue: customer.averageOrderValue default 0,
        totalOrders: customer.totalOrders default 0,
        lastOrderDate: customer.lastOrderDate,
        favoriteCategory: customer.favoriteCategory,
        lastPurchaseCategory: customer.lastPurchaseCategory
    },
    
    // Business rules and flags
    businessRules: applyBusinessRules(customer),
    
    // Customer preferences (if enabled)
    preferences: if (transformationConfig.includePreferences) 
        getCustomerPreferences(customer.customerId as String) 
    else null,
    
    // Metadata (if enabled)
    metadata: if (transformationConfig.includeMetadata) {
        transformedAt: now(),
        transformationVersion: "2.1.0",
        source: "customer-api",
        dataQuality: {
            completeness: calculateDataCompleteness(customer),
            validation: validateCustomerData(customer)
        }
    } else null
}

fun calculateDataCompleteness(customer: Object): Number = {
    var requiredFields = ["customerId", "firstName", "lastName", "email", "status"]
    var optionalFields = ["phone", "dateOfBirth", "address", "loyaltyPoints"]
    var allFields = requiredFields ++ optionalFields
    
    var presentFields = allFields filter (field) -> 
        customer[field] != null and customer[field] != ""
    
    (sizeOf(presentFields) / sizeOf(allFields)) * 100
}

fun groupCustomersBySegment(customers: Array): Object = 
    customers groupBy (customer) -> customer.accountInfo.tier

fun calculateSegmentStatistics(groupedCustomers: Object): Object = 
    groupedCustomers mapObject (segment, tierName) -> {
        (tierName): {
            count: sizeOf(segment),
            totalSpent: sum(segment map $.spendingProfile.totalSpent),
            averageSpent: avg(segment map $.spendingProfile.totalSpent),
            averageAge: avg(segment map $.personalInfo.age filter ($ != null)),
            topCategories: segment 
                map $.spendingProfile.favoriteCategory 
                filter ($ != null)
                groupBy ($)
                mapObject (categoryCustomers, category) -> {
                    (category): sizeOf(categoryCustomers)
                }
                orderBy (-$)
                take 3
        }
    }

// Main transformation logic
---
{
    // Process and transform all customers
    customers: customers 
        map enrichWithOrderHistory($)
        map formatCustomerOutput($)
        filter ($.metadata.dataQuality.validation.isValid or !transformationConfig.includeMetadata),
    
    // Segment analysis
    segmentAnalysis: if (transformationConfig.includeMetadata) {
        var transformedCustomers = customers 
            map enrichWithOrderHistory($)
            map formatCustomerOutput($)
            filter ($.metadata.dataQuality.validation.isValid)
        var groupedCustomers = groupCustomersBySegment(transformedCustomers)
        
        calculateSegmentStatistics(groupedCustomers) ++ {
            totalCustomers: sizeOf(transformedCustomers),
            segmentDistribution: groupedCustomers mapObject (segment, tierName) -> {
                (tierName): sizeOf(segment)
            }
        }
    } else null,
    
    // Transformation summary
    summary: {
        totalProcessed: sizeOf(customers),
        totalValid: sizeOf(customers map formatCustomerOutput($) filter (
            if (transformationConfig.includeMetadata) 
                $.metadata.dataQuality.validation.isValid 
            else true
        )),
        transformationErrors: customers 
            map formatCustomerOutput($)
            map $.metadata.dataQuality.validation
            filter (!$.isValid)
            map $.validationErrors,
        processedAt: now(),
        processingTimeMs: (now() - vars.startTime) as Number default 0
    },
    
    // Configuration used for this transformation
    configuration: transformationConfig
}