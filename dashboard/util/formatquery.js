function formatQuery(query, values) {
    let i = 0;
    return query.replace(/\?/g, () => {
        const val = values[i++];
        return typeof val === 'string' ? `'${val}'` : val;
    });
};

export default formatQuery;