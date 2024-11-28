insert into PublicationStats (publishMonth, 
    gender, 
    count,
    categoryId, 
    positionType,
    publisherId,
    type)
-- select dsitrubtion overall grouped by month


(SELECT 
    DATE_FORMAT(FROM_UNIXTIME(a.publishedAt / 1000), "%Y-%m-01") AS publishMonth, 
    ap.gender as gender, 
    COUNT(ap.id) AS count,
    NULL as categoryId,
    NULL as positionType,
    NULL as publisherId,
    "MENTION" as type
FROM ArticlePerson ap
JOIN Article a ON ap.articleId = a.id
JOIN Publisher p ON p.id = a.publisherId
JOIN PublisherCategory pc ON a.publisherCategoryId = pc.id
JOIN Category c ON pc.categoryId = c.id
WHERE FROM_UNIXTIME(a.publishedAt / 1000) BETWEEN '2022-01-01' AND '2024-12-31'
  AND ap.gender != 'DIVERS'
GROUP BY 
    ap.gender, 
    DATE_FORMAT(FROM_UNIXTIME(a.publishedAt / 1000), "%Y-%m")
ORDER BY 
    publishMonth, c.id, ap.gender DESC)

UNION

-- select dsitrubtion overall grouped by month and category

(SELECT 
    DATE_FORMAT(FROM_UNIXTIME(a.publishedAt / 1000), "%Y-%m-01") AS publishMonth, 
    ap.gender as gender, 
    COUNT(ap.id) AS count,
    c.id as categoryId,
    NULL as positionType,
    NULL as publisherId,
    "MENTION" as type
FROM ArticlePerson ap
JOIN Article a ON ap.articleId = a.id
JOIN Publisher p ON p.id = a.publisherId
JOIN PublisherCategory pc ON a.publisherCategoryId = pc.id
JOIN Category c ON pc.categoryId = c.id
WHERE FROM_UNIXTIME(a.publishedAt / 1000) BETWEEN '2022-01-01' AND '2024-12-31'
  AND ap.gender != 'DIVERS'
GROUP BY 
    ap.gender, 
    c.id, 
    DATE_FORMAT(FROM_UNIXTIME(a.publishedAt / 1000), "%Y-%m")
ORDER BY 
    publishMonth, c.id, ap.gender DESC)

UNION


-- select dsitrubtion overall grouped by month and category and high level positions

(SELECT 
    DATE_FORMAT(FROM_UNIXTIME(a.publishedAt / 1000), "%Y-%m-01") AS publishMonth, 
    ap.gender as gender, 
    COUNT(ap.id) AS count,
    c.id as categoryId,
    hlpt.positionType as positionType,
    NULL as publisherId,
    "MENTION" as type
FROM ArticlePerson ap
JOIN Article a ON ap.articleId = a.id
JOIN Publisher p ON p.id = a.publisherId
JOIN PublisherCategory pc ON a.publisherCategoryId = pc.id
JOIN Category c ON pc.categoryId = c.id
JOIN ArticlePersonText apt2 ON apt2.type = "occupation" AND apt2.articlePersonId = ap.id 
JOIN HighLevelPositionTrigger_ArticlePersonText_Match hlptAptMatch ON apt2.id = hlptAptMatch.articlePersonTextId
JOIN HighLevelPositionTrigger hlpt ON hlpt.id = hlptAptMatch.highLevelPositionTriggerId
WHERE FROM_UNIXTIME(a.publishedAt / 1000) BETWEEN '2022-01-01' AND '2024-12-31'
  AND ap.gender != 'DIVERS'
GROUP BY 
    ap.gender, 
    c.id, 
    DATE_FORMAT(FROM_UNIXTIME(a.publishedAt / 1000), "%Y-%m"),
    hlpt.positionType
ORDER BY 
    publishMonth, c.id, ap.gender DESC)

UNION


-- select dsitrubtion overall grouped by month and high level positions

(SELECT 
    DATE_FORMAT(FROM_UNIXTIME(a.publishedAt / 1000), "%Y-%m-01") AS publishMonth, 
    ap.gender as gender, 
    COUNT(ap.id) AS count,
    NULL as categoryId, 
    hlpt.positionType,
    NULL as publisherId,
    "MENTION" as type
FROM ArticlePerson ap
JOIN Article a ON ap.articleId = a.id
JOIN Publisher p ON p.id = a.publisherId
JOIN PublisherCategory pc ON a.publisherCategoryId = pc.id
JOIN Category c ON pc.categoryId = c.id
JOIN ArticlePersonText apt2 ON apt2.type = "occupation" AND apt2.articlePersonId = ap.id 
JOIN HighLevelPositionTrigger_ArticlePersonText_Match hlptAptMatch ON apt2.id = hlptAptMatch.articlePersonTextId
JOIN HighLevelPositionTrigger hlpt ON hlpt.id = hlptAptMatch.highLevelPositionTriggerId
WHERE FROM_UNIXTIME(a.publishedAt / 1000) BETWEEN '2022-01-01' AND '2024-12-31'
  AND ap.gender != 'DIVERS'
GROUP BY 
    ap.gender, 
    DATE_FORMAT(FROM_UNIXTIME(a.publishedAt / 1000), "%Y-%m"),
    hlpt.positionType
ORDER BY 
    publishMonth, c.id, ap.gender DESC)

UNION




-- select dsitrubtion overall grouped by month and category and high level positions

(SELECT 
    DATE_FORMAT(FROM_UNIXTIME(a.publishedAt / 1000), "%Y-%m-01") AS publishMonth, 
    ap.gender as gender, 
    COUNT(ap.id) AS count,
    c.id as categoryId, 
    'All' as positionType,
    NULL as publisherId,
    "MENTION" as type
FROM ArticlePerson ap
JOIN Article a ON ap.articleId = a.id
JOIN Publisher p ON p.id = a.publisherId
JOIN PublisherCategory pc ON a.publisherCategoryId = pc.id
JOIN Category c ON pc.categoryId = c.id
JOIN ArticlePersonText apt2 ON apt2.type = "occupation" AND apt2.articlePersonId = ap.id 
JOIN HighLevelPositionTrigger_ArticlePersonText_Match hlptAptMatch ON apt2.id = hlptAptMatch.articlePersonTextId
JOIN HighLevelPositionTrigger hlpt ON hlpt.id = hlptAptMatch.highLevelPositionTriggerId
WHERE FROM_UNIXTIME(a.publishedAt / 1000) BETWEEN '2022-01-01' AND '2024-12-31'
  AND ap.gender != 'DIVERS'
GROUP BY 
    ap.gender, 
    c.id, 
    DATE_FORMAT(FROM_UNIXTIME(a.publishedAt / 1000), "%Y-%m")
ORDER BY 
    publishMonth, c.id, ap.gender DESC)

UNION


-- select dsitrubtion overall grouped by month and high level positions

(SELECT 
    DATE_FORMAT(FROM_UNIXTIME(a.publishedAt / 1000), "%Y-%m-01") AS publishMonth, 
    ap.gender as gender, 
    COUNT(ap.id) AS count,
    NULL as categoryId, 
    'All' as positionType,
    NULL as publisherId,
    "MENTION" as type
FROM ArticlePerson ap
JOIN Article a ON ap.articleId = a.id
JOIN Publisher p ON p.id = a.publisherId
JOIN PublisherCategory pc ON a.publisherCategoryId = pc.id
JOIN Category c ON pc.categoryId = c.id
JOIN ArticlePersonText apt2 ON apt2.type = "occupation" AND apt2.articlePersonId = ap.id 
JOIN HighLevelPositionTrigger_ArticlePersonText_Match hlptAptMatch ON apt2.id = hlptAptMatch.articlePersonTextId
JOIN HighLevelPositionTrigger hlpt ON hlpt.id = hlptAptMatch.highLevelPositionTriggerId
WHERE FROM_UNIXTIME(a.publishedAt / 1000) BETWEEN '2022-01-01' AND '2024-12-31'
  AND ap.gender != 'DIVERS'
GROUP BY 
    ap.gender, 
    DATE_FORMAT(FROM_UNIXTIME(a.publishedAt / 1000), "%Y-%m")
ORDER BY 
    publishMonth, c.id, ap.gender DESC)




