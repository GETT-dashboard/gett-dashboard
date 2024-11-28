create table HighLevelPositionTrigger_ArticlePersonText_Match(
    highLevelPositionTriggerId int(11) NOT NULL,
    articlePersonTextId int(11) NOT NULL
)

ALTER TABLE HighLevelPositionTrigger_ArticlePersonText_Match
ADD CONSTRAINT fk_highLevelPositionTriggerId
FOREIGN KEY (highLevelPositionTriggerId)
REFERENCES HighLevelPositionTrigger(id);


ALTER TABLE HighLevelPositionTrigger_ArticlePersonText_Match
ADD CONSTRAINT fk_articlePersonTextId
FOREIGN KEY (articlePersonTextId)
REFERENCES ArticlePersonText(id);

ALTER TABLE HighLevelPositionTrigger_ArticlePersonText_Match
ADD CONSTRAINT unique_highLevelPositionTrigger_articlePersonText
UNIQUE (highLevelPositionTriggerId, articlePersonTextId);

CREATE INDEX idx_positionType ON HighLevelPositionTrigger (positionType);