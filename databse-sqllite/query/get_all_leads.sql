SELECT 
    L.LeadID,
    L.FirstName,
    L.LastName,
    L.Phone,
    L.Email,
    L.Address,
    L.City,
    L.State,
    L.PinCode,
    L.Country,
    L.ProductId,
    L.AccountId,
    R.RatingValue,
    R.Description AS RatingDescription,
    C.CampaignID,
    C.CampaignName
FROM 
    Leads L
JOIN 
    Rating R ON L.RatingId = R.RatingId  -- Assuming Leads table has a RatingId column
JOIN 
    Campaign C ON L.CampaignID = C.CampaignID  -- Assuming Leads table has a CampaignID column
ORDER BY 
    L.LeadID;  -- You can change the ordering as needed
