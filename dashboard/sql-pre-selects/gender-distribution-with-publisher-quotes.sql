-- select dsitrubtion overall grouped by month


(SELECT 
    DATE_FORMAT(FROM_UNIXTIME(a.publishedAt / 1000), "%Y-%m-01") AS publishMonth, 
    ap.gender as gender, 
    COUNT(apt.id) AS count,
    NULL as categoryId, 
    NULL as positionType,
    p.id as publisherId,
    "QUOTE" as type
FROM ArticlePersonText apt
JOIN ArticlePerson ap on apt.articlePersonId = ap.id and apt.type = "QUOTE"
JOIN Article a ON ap.articleId = a.id
JOIN Publisher p ON p.id = a.publisherId
JOIN PublisherCategory pc ON a.publisherCategoryId = pc.id
JOIN Category c ON pc.categoryId = c.id
WHERE FROM_UNIXTIME(a.publishedAt / 1000) BETWEEN '2022-01-01' AND '2024-12-31'
  AND ap.gender != 'DIVERS'
GROUP BY 
    ap.gender, 
    DATE_FORMAT(FROM_UNIXTIME(a.publishedAt / 1000), "%Y-%m"),
    p.id
ORDER BY 
    publishMonth, c.id, ap.gender DESC)

UNION

-- select dsitrubtion overall grouped by month and category

(SELECT 
    DATE_FORMAT(FROM_UNIXTIME(a.publishedAt / 1000), "%Y-%m-01") AS publishMonth, 
    ap.gender as gender, 
    COUNT(apt.id) AS count,
    c.id as categoryId, 
    NULL as positionType,
    p.id as publisherId,
    "QUOTE" as type
FROM ArticlePersonText apt
JOIN ArticlePerson ap on apt.articlePersonId = ap.id and apt.type = "QUOTE"
JOIN Article a ON ap.articleId = a.id
JOIN Publisher p ON p.id = a.publisherId
JOIN PublisherCategory pc ON a.publisherCategoryId = pc.id
JOIN Category c ON pc.categoryId = c.id
WHERE FROM_UNIXTIME(a.publishedAt / 1000) BETWEEN '2022-01-01' AND '2024-12-31'
  AND ap.gender != 'DIVERS'
GROUP BY 
    ap.gender, 
    c.id, 
    DATE_FORMAT(FROM_UNIXTIME(a.publishedAt / 1000), "%Y-%m"),
    p.id
ORDER BY 
    publishMonth, c.id, ap.gender DESC)

UNION


-- select dsitrubtion overall grouped by month and category and high level positions

(SELECT 
    DATE_FORMAT(FROM_UNIXTIME(a.publishedAt / 1000), "%Y-%m-01") AS publishMonth, 
    ap.gender as gender, 
    COUNT(apt.id) AS count,
    c.id as categoryId, 
    hlpt.positionType as positionType,
    p.id as publisherId,
    "QUOTE" as type
FROM ArticlePersonText apt
JOIN ArticlePerson ap on apt.articlePersonId = ap.id and apt.type = "QUOTE"
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
    hlpt.positionType,
    p.id
ORDER BY 
    publishMonth, c.id, ap.gender DESC)

UNION


-- select dsitrubtion overall grouped by month and high level positions

(SELECT 
    DATE_FORMAT(FROM_UNIXTIME(a.publishedAt / 1000), "%Y-%m-01") AS publishMonth, 
    ap.gender as gender, 
    COUNT(apt.id) AS count,
    NULL as categoryId, 
    hlpt.positionType,
    p.id as publisherId,
    "QUOTE" as type
FROM ArticlePersonText apt
JOIN ArticlePerson ap on apt.articlePersonId = ap.id and apt.type = "QUOTE"
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
    hlpt.positionType,
    p.id
ORDER BY 
    publishMonth, c.id, ap.gender DESC)

UNION




-- select dsitrubtion overall grouped by month and category and high level positions

(SELECT 
    DATE_FORMAT(FROM_UNIXTIME(a.publishedAt / 1000), "%Y-%m-01") AS publishMonth, 
    ap.gender as gender, 
    COUNT(apt.id) AS count,
    c.id as categoryId, 
    'All' as positionType,
    p.id as publisherId,
    "QUOTE" as type
FROM ArticlePersonText apt
JOIN ArticlePerson ap on apt.articlePersonId = ap.id and apt.type = "QUOTE"
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
    p.id
ORDER BY 
    publishMonth, c.id, ap.gender DESC)

UNION


-- select dsitrubtion overall grouped by month and high level positions

(SELECT 
    DATE_FORMAT(FROM_UNIXTIME(a.publishedAt / 1000), "%Y-%m-01") AS publishMonth, 
    ap.gender as gender, 
    COUNT(apt.id) AS count,
    NULL as categoryId, 
    'All' as positionType,
    p.id as publisherId,
    "QUOTE" as type
FROM ArticlePersonText apt
JOIN ArticlePerson ap on apt.articlePersonId = ap.id and apt.type = "QUOTE"
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
    p.id
ORDER BY 
    publishMonth, c.id, ap.gender DESC)


