from preprocessing import manualOperations
from preprocessing.manualOperations import TEXT_PART_SEPERATOR

# testString = """Nach dem ersten Schaulaufen beim 2:1 gegen die Tschechen muss man zwischenbilanzieren: In wohl keinem Moment seiner Karriere verlor Ronaldo den Vergleich mit Messi so deutlich wie jetzt. Das liegt an seiner größeren Abhängigkeit von der Physis. Zugespitzt: Messi ist ein Genie, Ronaldo ein Athlet. Würde sich der Argentinier selbst humpelnd noch einen Zuckerpass aus dem Fußgelenk schütteln, wirkt Ronaldo ohne Spritzigkeit wie ein Kicker von der traurigen Gestalt."""
testString = """Die Pumps in der Wüste waren ein politisches Signal

Die viel kritisierten hochhackigen Pumps, mit denen sie in Mali durch das Wüstenlager der Bundeswehr stapfte, waren deshalb kein Modestatement, sondern das politische Signal einer Frau, die im linken SPD-Bezirk Hessen-Süd sozialisiert wurde."""
# testString = """»Cristiano ist bei der Nationalelf wegen seiner Verdienste«, insistierte der Trainer dieser Tage und erinnerte an 50 Saisontore für Al-Nassr: »Niemand wird hier nur wegen des Namens berufen.« Doch Martínez hat auch Privilegien gestutzt. Anders als früher darf Ronaldos Entourage engster Freunde und Agenten nicht mit im Teamhotel residieren. Der Superstar sei dadurch zugänglicher für seine Kollegen, heißt es. »Unfassbar wichtig« nannte Vitinha die Erfahrung von Ronaldo und Innenverteidiger Pepe, mit 41 nun ältester Spieler der WM-Geschichte: »Ich fühle mich geehrt, mit ihnen zu spielen.«"""

splitted = manualOperations.splitIntoSentences(TEXT_PART_SEPERATOR + TEXT_PART_SEPERATOR + testString)

print(splitted)