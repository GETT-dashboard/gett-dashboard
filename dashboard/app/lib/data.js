// Example usage in a Next.js API route
'use server'
import connection from './db';
import formatQuery from './../../util/formatquery';
import 'server-only';

function getPublisherCondition(publisher) {
    return publisher !== '' && publisher !== 'All' ? `p.name = ?` : '1=1';
}

// import { getSessionUserId } from './session'; // Assuming we have a function to get the session user ID

export async function genderMentionByMonth(startDate, endDate, categoryId, publisherId, positionType) {
    // const userId = await getSessionUserId();
    // if (publisherId !== '' && publisherId !== 'All' && userId !== publisherId) {
        publisherId = '';
    // }
    try {
        // Format the startDate and endDate for SQL
        startDate = startDate.toISOString().slice(0, 10);
        endDate = endDate.toISOString().slice(0, 10);

        // Initialize the query parameters
        const values = [startDate, endDate];

        // Prepare conditions and dynamic query parts
        // Publisher condition
        const publisherCondition = (publisherId !== '' && publisherId !== 'All') ? `AND ps.publisherId = ?` : ' AND ps.publisherId is NULL';
        if (publisherId !== '' && publisherId !== 'All') values.push(publisherId);

        // Category condition
        const categoryCondition = (categoryId !== '' && categoryId !== 'All') ? `AND ps.categoryId = ?` : 'AND ps.categoryId is NULL';
        if (categoryId !== '' && categoryId !== 'All') values.push(categoryId);

        // Position type condition
        const positionTypeCondition = (positionType !== '') ? `AND ps.positionType = ?` : 'AND ps.positionType is NULL';
        if (positionType !== '') values.push(positionType);

        const categorySelect = (categoryId !== '' && categoryId !== 'All') ? `ps.categoryId AS categoryId,` : '';
        const categoryGroup = (categoryId !== '' && categoryId !== 'All') ? `, ps.categoryId` : '';
        const publisherSelect = (publisherId !== '' && publisherId !== 'All') ? `ps.publisherId AS publisherId,` : '';
        const publisherSelectGenderTotals = (publisherId !== '' && publisherId !== 'All') ? `gt.publisherId AS publisherId,` : '';
        const publisherGroup = (publisherId !== '' && publisherId !== 'All') ? `, ps.publisherId` : '';
        const publisherNameConcat = (publisherId !== '' && publisherId !== 'All') ? `CONCAT(' (', gt.publisherId, ')')` : `''`;

        // Define the query
        const query = `
        WITH gender_totals AS (
            SELECT
                ps.publishMonth,
                ps.gender,
                ${categorySelect}
                ${publisherSelect}
                SUM(ps.count) AS gender_count,
                SUM(SUM(ps.count)) OVER (PARTITION BY ps.publishMonth ${categoryGroup} ${publisherGroup}) AS total_count
            FROM
                PublicationStats ps
            WHERE
                ps.publishMonth BETWEEN ? AND ?
                AND ps.gender IN ('FEMALE', 'MALE')
				AND ps.type = 'MENTION'
                ${categoryCondition}
                ${publisherCondition}
                ${positionTypeCondition}
            GROUP BY
                ps.publishMonth, ps.gender ${categoryGroup} ${publisherGroup}
        )
        SELECT
            DATE_FORMAT(gt.publishMonth, "%Y-%m") AS date,
            ${publisherSelectGenderTotals}
            ROUND((gt.gender_count / gt.total_count) * 100, 0) AS total,
            gt.total_count,
            CONCAT('Anteil ', CASE WHEN gt.gender = 'FEMALE' THEN 'Frauen' ELSE 'Männer' END, ${publisherNameConcat}) AS name
        FROM
            gender_totals gt
        ORDER BY
            gt.publishMonth ASC, gt.gender;
        `;

        // Log the query for debugging
        console.log(formatQuery(query, values));

        // Execute the query
        const [rows] = await connection.promise().execute(query, values);

        // Log and return the results
        // console.log(rows);
        return rows.map(value => {
            value.total_count = parseInt(value.total_count);
            return value;
        });
    } catch (error) {
        console.error('Error executing MySQL query:', error);
        throw new Error('Error executing query');
    }
}


export async function genderMentionOverall(startDate, endDate, publisherId, categoryId, positionType) {
    try {
        publisherId = '';

        // Convert start and end dates to ISO strings
        startDate = startDate.toISOString().slice(0, 10);
        endDate = endDate.toISOString().slice(0, 10);

        // Initialize the values array
        const values = [startDate, endDate];

        // Publisher condition
        const publisherCondition = (publisherId !== '' && publisherId !== 'All') ? `AND ps.publisherId = ?` : ' AND ps.publisherId is NULL';
        if (publisherId !== '' && publisherId !== 'All') values.push(publisherId);

        // Category condition
        const categoryCondition = (categoryId !== '' && categoryId !== 'All') ? `AND ps.categoryId = ?` : 'AND ps.categoryId is NULL';
        if (categoryId !== '' && categoryId !== 'All') values.push(categoryId);

        // Position type condition
        const positionTypeCondition = (positionType !== '') ? `AND ps.positionType = ?` : 'AND ps.positionType is NULL';
        if (positionType !== '') values.push(positionType);

        // Construct the query
        const query = `
        SELECT 
            ps.gender, 
            SUM(ps.count) AS total
        FROM 
            PublicationStats ps
        WHERE 
            ps.publishMonth BETWEEN ? AND ?
            AND ps.gender IN ('FEMALE', 'MALE')
			AND ps.type = 'MENTION'
            ${publisherCondition}
            ${categoryCondition}
            ${positionTypeCondition}
        GROUP BY 
            ps.gender
        ORDER BY 
            ps.gender;
        `;

        // Log the query for debugging
        console.log(formatQuery(query, values));

        // Execute the query
        const [rows] = await connection.promise().execute(query, values);

        // Log and return the results
        // console.log(rows);
        return rows.map(value => {
            value.total = parseInt(value.total);
            return value;
        });
    } catch (error) {
        console.error('Error executing MySQL query:', error);
        throw new Error('Error executing query');
    }
}




export async function singlePersonMentionByMonth(startDate, endDate, people) {
	try {
		// Convert start and end dates to ISO strings
		startDate = startDate.toISOString().slice(0, 10);
		endDate = endDate.toISOString().slice(0, 10);

		// Prepare an array for query values
		const values = [startDate, endDate];

		// Dynamic IN clause for people list
		const peoplePlaceholders = people.map(() => '?').join(', ');
		values.push(...people);

		// Query with placeholders
		const query = `
            SELECT name, LEFT(FROM_UNIXTIME(a.publishedAt / 1000), 7) AS date, COUNT(*) AS total 
            FROM ArticlePerson ap 
            JOIN Article a ON ap.articleId = a.id 
            WHERE FROM_UNIXTIME(a.publishedAt / 1000) BETWEEN ? AND ? 
            AND name IN (${peoplePlaceholders}) 
            GROUP BY name, date
            ORDER BY date ASC;
        `;

		// Execute query with parameterized values
		const [rows] = await connection.promise().execute(query, values);
		// console.log(formatQuery(query, values));
		// console.log(rows);
		return rows;
	} catch (error) {
		console.error('Error executing MySQL query:', error);
		throw new Error('Error executing query');
	}
}


export async function totalNumberOfArticles(startDate, endDate) {
	try {
		// Convert start and end dates to ISO strings
		startDate = startDate.toISOString().slice(0, 10);
		endDate = endDate.toISOString().slice(0, 10);

		// Prepare an array for query values
		const values = [startDate, endDate];

		let query = `select count(*) as total from  Article a  where FROM_UNIXTIME(a.publishedAt / 1000) BETWEEN ? AND ? ;`
		const [rows, fields] = await connection.promise().execute(query, values);
		// console.log(query)
		// console.log(rows);
		return rows;
	} catch (error) {
		console.error('Error executing MySQL query:', error);
		throw new Error('Error executing query');
	}
}

export async function genderMentionByCategory(startDate, endDate, publisherId, positionType) {
    try {
        publisherId = '';

        // Convert start and end dates to strings
        startDate = startDate.toISOString().slice(0, 10);
        endDate = endDate.toISOString().slice(0, 10);

        // Initialize values array for parameterized query
        const values = [startDate, endDate];

        // Publisher condition
        const publisherCondition = publisherId !== '' && publisherId !== 'All'
            ? `ps.publisherId = ?`
            : 'ps.publisherId IS NULL';
        if (publisherId !== '' && publisherId !== 'All') values.push(publisherId);

        // PositionType condition
        const positionTypeCondition = positionType !== ''
            ? `ps.positionType = ?`
            : 'ps.positionType is NULL';
        if (positionType !== '') values.push(positionType);

        // Final query string with placeholders
        const query = `
            SELECT 
                ps.gender,
                ps.categoryId AS categoryId,
                ROUND(SUM(ps.count) * 100.0 / SUM(SUM(ps.count)) OVER (PARTITION BY ps.categoryId), 2) AS percentage
            FROM 
                PublicationStats ps
            WHERE 
                ps.publishMonth BETWEEN ? AND ?
                AND ps.gender IN ('FEMALE', 'MALE')
                AND ${publisherCondition}
                AND ${positionTypeCondition}
				AND ps.categoryId is NOT NULL
				AND ps.type = 'MENTION'
            GROUP BY 
                ps.gender, ps.categoryId
            ORDER BY 
                percentage DESC;
        `;

        // Log the formatted query
        // console.log('Executing query:', formatQuery(query, values));

        // Execute the query with values
        const [rows] = await connection.promise().execute(query, values);

        // Log and return the results
        // console.log(rows);
        return rows;
    } catch (error) {
        console.error('Error executing MySQL query:', error);
        throw new Error('Error executing query');
    }
}



export async function genderQuoteOverall(startDate, endDate, publisherId, categoryId, positionType) {
	try {
        publisherId = '';

        // Convert start and end dates to ISO strings
        startDate = startDate.toISOString().slice(0, 10);
        endDate = endDate.toISOString().slice(0, 10);

        // Initialize the values array
        const values = [startDate, endDate];

        // Publisher condition
        const publisherCondition = (publisherId !== '' && publisherId !== 'All') ? `AND ps.publisherId = ?` : ' AND ps.publisherId is NULL';
        if (publisherId !== '' && publisherId !== 'All') values.push(publisherId);

        // Category condition
        const categoryCondition = (categoryId !== '' && categoryId !== 'All') ? `AND ps.categoryId = ?` : 'AND ps.categoryId is NULL';
        if (categoryId !== '' && categoryId !== 'All') values.push(categoryId);

        // Position type condition
        const positionTypeCondition = (positionType !== '') ? `AND ps.positionType = ?` : 'AND ps.positionType is NULL';
        if (positionType !== '') values.push(positionType);

        // Construct the query
        const query = `
        SELECT 
            ps.gender, 
            SUM(ps.count) AS total
        FROM 
            PublicationStats ps
        WHERE 
            ps.publishMonth BETWEEN ? AND ?
            AND ps.gender IN ('FEMALE', 'MALE')
			AND ps.type = 'QUOTE'
            ${publisherCondition}
            ${categoryCondition}
            ${positionTypeCondition}
        GROUP BY 
            ps.gender
        ORDER BY 
            ps.gender;
        `;

        // Log the query for debugging
        // console.log(formatQuery(query, values));

        // Execute the query
        const [rows] = await connection.promise().execute(query, values);

        // Log and return the results
        // console.log(rows);
        return rows.map(value => {
            value.total = parseInt(value.total);
            return value;
        });
    } catch (error) {
        console.error('Error executing MySQL query:', error);
        throw new Error('Error executing query');
    }
}

export async function fetchCategoryList() {
	try {
		let query = `                
                  select c.id as id, c.value as name from Category c;`
		const [rows, fields] = await connection.promise().execute(query);
		// console.log(query)
		// console.log(rows);
		return rows;
	} catch (error) {
		console.error('Error executing MySQL query:', error);
		throw new Error('Error executing query');
	}
}

export async function fetchPersonList() {
	try {
		let query = `                
                    select name from  ArticlePerson ap join Article a on ap.articleId = a.id  group by 1 order by count(*) desc limit 500;`
		const [rows, fields] = await connection.promise().execute(query);
		// console.log(query)
		// console.log(rows);
		return rows;
	} catch (error) {
		console.error('Error executing MySQL query:', error);
		throw new Error('Error executing query');
	}
}



export async function fetchPublisherList(publisher) {
	try {
        return []; 
		// let values = [];
		// const publisher_condition = getPublisherCondition(publisher);
		// if (publisher !== '' && publisher !== 'All') values.push(publisher);
		// let query = `                
        //               select id, name from Publisher p where ${publisher_condition};`
		// const [rows, fields] = await connection.promise().execute(query, values);
		// console.log(query)
		// console.log(rows);
		// return rows;
	} catch (error) {
		console.error('Error executing MySQL query:', error);
		throw new Error('Error executing query');
	}
}

// export async function fetchRegexList(highlevelpostion) {
// 	try {
// 		if (highlevelpostion === 'None') { return []; }

// 		// Prepared statement query with placeholder
// 		const query = `SELECT regexValue FROM HighLevelPositionTrigger WHERE positionType = ?`;

// 		// Execute the query with the provided highlevelpostion parameter
// 		const [rows] = await connection.promise().execute(query, [highlevelpostion]);

// 		console.log(rows);
// 		return rows;
// 	} catch (error) {
// 		console.error('Error executing MySQL query:', error);
// 		throw new Error('Error executing query');
// 	}
// }
