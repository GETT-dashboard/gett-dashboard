function adaptToGerman(gender){
    return gender == 'FEMALE' ? 'Frauen' : gender == 'MALE' ?  'Männer' : 'UNKNOWN';
}
export default adaptToGerman;