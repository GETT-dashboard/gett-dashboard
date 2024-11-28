CREATE TABLE PublicationStats (
    publishMonth DATE NOT NULL, -- Column for storing "YYYY-MM" values
    gender ENUM('FEMALE', 'MALE') NOT NULL, -- Column restricted to "FEMALE" or "MALE"
    count INT NOT NULL, -- Column for storing counts
    categoryId INT DEFAULT NULL, -- Nullable Category ID
    positionType ENUM('All', 'economy', 'science', 'other', 'politic') DEFAULT NULL, -- Nullable position type
    publisherId INT DEFAULT NULL, -- Nullable Publisher ID,
    type ENUM('MENTION','QUOTE') NOT NULL,
    UNIQUE KEY unique_stats (
        publishMonth, 
        gender, 
        categoryId, 
        positionType, 
        publisherId,
        type
    ), -- Complex unique key
    INDEX idx_publishMonth (publishMonth), -- Index on publishMonth
    INDEX idx_gender (gender), -- Index on gender
    INDEX idx_categoryId (categoryId), -- Index on categoryId
    INDEX idx_positionType (positionType), -- Index on positionType
    INDEX idx_publisherId (publisherId) -- Index on publisherId
);
