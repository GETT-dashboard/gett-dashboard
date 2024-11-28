SELECT 
    DATE_FORMAT(FROM_UNIXTIME(a.publishedAt / 1000), "%Y-%m") AS publishMonth, 
    COUNT(ap.name) AS nameCount, 
    ap.name
FROM 
    ArticlePerson ap
JOIN 
    Article a 
ON 
    ap.articleId = a.id
WHERE 
    ap.name IN (
        SELECT 
            ap_sub.name 
        FROM 
            ArticlePerson ap_sub
        JOIN 
            Article a_sub 
        ON 
            ap_sub.articleId = a_sub.id
        WHERE 
            ap_sub.gender != 'DIVERS'
        GROUP BY 
            ap_sub.name
        HAVING 
            COUNT(ap_sub.name) > 24
    )
GROUP BY 
    publishMonth, ap.name
ORDER BY 
    nameCount DESC;
