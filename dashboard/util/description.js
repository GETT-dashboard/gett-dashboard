import HighLevelPositions from "./highlevelpositions";

const months = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]

function dateToDisplayMonthYear(start_date) {
    return months[start_date.getMonth()] + " " + start_date.getFullYear();
}

const displayForValueOfHighLevelPosition = (value) => {
    return HighLevelPositions.filter(pos => pos.value == value)[0].display;
}

function createDescription(start_date, end_date, data, selectedChart, publisherId = '', category = '', highlevelposition = '', total_count = '') {
    let startDate = dateToDisplayMonthYear(start_date)
    let endDate = dateToDisplayMonthYear(end_date)
    let description = '';

    const categoryDesc = (category && category !== 'All') ? ` im Ressort "${category}" ` : ''
    const fullDataSet = category === 'All' ? " gesamten" : '';
    const publisherDesc = publisherId ? ` in Veröffentlichungen von "${publisherId}" ` : ''
    const highlevelpostionDesc = highlevelposition ? ` in Spitzenpositionen (in ${displayForValueOfHighLevelPosition(highlevelposition)}) ` : ''
    if (selectedChart == 'mentionPieChart') {

        const totalCount = data.reduce((sum, item) => sum + item.total, 0);

        // Get female count
        const femaleCount = data.find(item => item.gender === 'FEMALE').total;

        // Calculate female percentage
        const percentage = ((femaleCount / totalCount) * 100).toFixed(0);
        // description = `In the time frame ${startDate} to ${endDate}, ${percentage}% females (out of ${totalCount} in total) names were mentioned`;
        // description = `Im Zeitraum von ${startDate} bis ${endDate} beträgt der Anteil von namentlich genannten Frauen ${highlevelpostionDesc}${cateoryDesc}${publisherDesc}im Analysedatendatz ${percentage}% (insgesamt ${totalCount.toLocaleString()} Personen erkannt)`;
        description = `Im Zeitraum von ${startDate} bis ${endDate} betrug der Anteil von namentlich genannten Frauen ${highlevelpostionDesc}${categoryDesc}${publisherDesc} im${fullDataSet} Analysedatendatz ${percentage}% (insgesamt ${totalCount.toLocaleString()} Personen erkannt).`;
        

    }

    else if (selectedChart == 'personLineChart') {

        const totalCount_overall = total_count[0].total

        const result = data.reduce((acc, item) => {
            const existing = acc.find(entry => entry.name === item.name);
            if (existing) {
                existing.total += item.total;
            } else {
                acc.push({ name: item.name, total: item.total });
            }
            return acc;
        }, []);

        // Generate output string
        const names = result.map(item => item.name).join(', ');
        const totalCount = result.reduce((sum, item) => sum + item.total, 0);
        // description = `In the time frame ${startDate} to ${endDate}, number of articles mentioning ${names} was  ${totalCount} vs ${totalCount_overall} total articles`;
        description = `Im Zeitraum von ${startDate} bis ${endDate} wurden die Personen "${names}" insgesamt ${totalCount.toLocaleString()} mal ${highlevelpostionDesc}${categoryDesc}${publisherDesc} namentlich genannt in insgesamt ${totalCount_overall.toLocaleString()} Artikeln des Analysedatendatz.`;

    }

    else if (selectedChart == 'genderCategoryBarChart') {

        const totalGender = total_count
            .filter(item => item.gender !== 'DIVERS')  // Exclude 'DIVERS'
            .reduce((sum, item) => sum + item.total, 0);

        // Find the percentage for each gender
        const male = total_count.find(item => item.gender === 'MALE').total;
        const female = total_count.find(item => item.gender === 'FEMALE').total;

        const malePercentage = ((male / totalGender) * 100).toFixed(0);
        const femalePercentage = ((female / totalGender) * 100).toFixed(0);
        // description = `In the time frame ${startDate} to ${endDate}, the overall distribution of gender was ${malePercentage}% males vs ${femalePercentage}% females`;
        description = `Im Zeitraum von ${startDate} bis ${endDate} wurden insgesamt ${totalGender.toLocaleString()} Personen namentlich im Analysedatendatz genannt. Der Anteil von Frauen betrug in diesem Zeitraum ${femalePercentage}%.`;

    }

    else if (selectedChart == 'genderLineChart') {

        const filteredData = data.filter(item => item.name === "Anteil Frauen");

        const totals = filteredData.map(item => parseFloat(item.total));

        // const totals = data.map(item => parseFloat(item.total));

        // Get minimum and maximum values
        const minTotal = Math.min(...totals).toFixed(0);
        const maxTotal = Math.max(...totals).toFixed(0);
        // description = `In the time frame ${startDate} to ${endDate}, the minimum total mentions were ${minTotal}% and the maximum total mentions were ${maxTotal}% for women `;
        description = `Im Zeitraum von ${startDate} bis ${endDate} betrug der Anteil von namentlich genannten Frauen ${highlevelpostionDesc} eines Monat mindestens ${minTotal}% und maximal ${maxTotal}% ${categoryDesc}${publisherDesc} im${fullDataSet} Analysedatendatz.`;

    }

    else if (selectedChart == 'quotePieChart') {

        const totalCount = data.reduce((sum, item) => sum + item.total, 0);

        // Get female count
        const femaleCount = data.find(item => item.gender === 'FEMALE').total;

        // Calculate female percentage
        const percentage = ((femaleCount / totalCount) * 100).toFixed(0);
        // description = `In the time frame ${startDate} to ${endDate}, ${percentage}% of quotes were attributed to females (out of ${totalCount} in total) `;
        // description = `Im Zeitraum von ${startDate} bis ${endDate} beträgt der Anteil von Frauen an Zitaten ${highlevelpostionDesc}${cateoryDesc}${publisherDesc}die namentlich genannten Personen zugeordnet wurden im Analysedatendatz ${percentage}% (insgesamt ${totalCount.toLocaleString()} Zitate erkannt)`;
        description = `Im Zeitraum von ${startDate} bis ${endDate} betrug der Anteil direkter Zitate von Frauen ${highlevelpostionDesc}${categoryDesc}${publisherDesc} im Analysedatendatz ${percentage}% (insgesamt ${totalCount.toLocaleString()} Zitate erkannt).`;

    }

    else if(selectedChart == 'stereotypePieChart'){

        const groupedData = data.reduce((acc, item) => {
            const { stereo, gender } = item;
            if (!acc[stereo]) acc[stereo] = { MALE: 0, FEMALE: 0 };
            acc[stereo][gender] += item['count(ap.name)'];
            return acc;
          }, {});
        
          // Generate strings for each stereotype
          const stereotypeDescriptions = Object.entries(groupedData).map(([stereo, counts]) =>
            `For stereotype ${stereo}, there are ${counts.MALE} males vs ${counts.FEMALE} females.`
          ).join(' ');
        
          // Combine the hardcoded intro with the descriptions
          return `From the date ${startDate} to ${endDate} , ${stereotypeDescriptions}`;

    }


    return description;
}

export default createDescription;
