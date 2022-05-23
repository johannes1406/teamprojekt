from flask import Flask, request

app = Flask(__name__)
import time
import re
import random


import smtplib
# from email.mime.text import MIMEText


@app.route('/')  # this is the home page route
def hello_world():  # this is the home page function that generates the page code
    return "Teamprojekt"


# webhook call Methode
@app.route('/webhook', methods=['POST'])
def webhook():
    # server sachen
    req = request.get_json(silent=True, force=True)
    query_result = req.get('queryResult')

    # Methode um Kontext von Fragen entgegenzunehmen und wieder richtig zu setzen - fertig
    def setContext():
        print("Set Context ")
        i = 0
        dummie = ""
        help = [""]

        try:
            while True:
                dummie = query_result.get('outputContexts')[i].get('name')
                i = i + 1
        except Exception:
            print("Exception")

        while (i > 1):
            help.append("")
            i = i - 1
        i = 0

        try:
            while True:
                dummie = query_result.get('outputContexts')[i].get('name')
                if '/contexts/variable' in str(query_result.get('outputContexts')[i].get('name')):
                    help[i] = {"name": dummie, "lifespanCount": 50}
                elif '/contexts/__system_counters__' in str(query_result.get('outputContexts')[i].get('name')):
                    help[i] = {"name": dummie, "lifespanCount": 0}
                else:
                    help[i] = {"name": dummie, "lifespanCount": 1}

                i = i + 1

        except Exception:
            return help
        return help

        # Methode String Variablenabfrage Kontext variable

    def getVariableStr(var):
        dummie = ""
        i = 0
        while (dummie == "" or dummie == "None"):
            if '/contexts/variable' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = str(query_result.get('outputContexts')[i].get('parameters').get(str(var)))
                break
            i = i + 1
        return dummie

    # Methode Int Variablenabfrage Kontext variable
    def getVariableInt(var):
        dummie = 0
        i = 0
        while (dummie == 0):
            if '/contexts/variable' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = int(round(query_result.get('outputContexts')[i].get('parameters').get(str(var)), 0))
                break
            i = i + 1
        print(str(var))
        return dummie

    # Methode um Versicherungsbetrag zu berechnen. Liefert String zurück
    def rechnerVersicherungsbetrag(groesse):
        versicherungsbetrag_einrichtungswert = groesse * 650
        str_versicherungsbetrag_einrichtungswert = str(versicherungsbetrag_einrichtungswert)
        print(str_versicherungsbetrag_einrichtungswert)
        str_versicherungsbetrag_einrichtungswert = str_versicherungsbetrag_einrichtungswert.replace('.', ',')
        if ',' in str_versicherungsbetrag_einrichtungswert:
            str_versicherungsbetrag_einrichtungswert = re.sub(r'(?<!^)(?=(\d{3})+,)', r'..',
                                                              str_versicherungsbetrag_einrichtungswert)
        else:
            str_versicherungsbetrag_einrichtungswert = re.sub(r'(?<!^)(?=(\d{3})+$)', r'..',
                                                              str_versicherungsbetrag_einrichtungswert)
        return str_versicherungsbetrag_einrichtungswert

    # Methode zum Angeben der richtigen Versicherungssumme inklusive Selbstbehalt
    def versicherungssummeMitZusatz():
        versicherungssumme = 0
        zusatz = getVariableStr('zusatz').title()
        v_help = 0
        v2_help = 0

        try:
            v_help = getVariableInt('abfrage_versicherungssumme')
        except Exception:
            print("Fehler abfrage_versicherungssumme")
        try:
            v2_help = getVariableInt('aendern_versicherungssumme')
        except Exception:
            print("Fehler aendern_versicherungssumme")

        if v2_help != 0:
            versicherungssumme = v2_help
        elif v_help != 0:
            versicherungssumme = v_help
        else:
            versicherungssumme = int(getVariableInt('groesse') * 650)

        if zusatz == "Glas":
            versicherungssumme = versicherungssumme + 14720
        elif zusatz == "Fahrrad":
            versicherungssumme = versicherungssumme + 9200
        elif zusatz == "Beide":
            versicherungssumme = versicherungssumme + 23000

        return versicherungssumme

    # Methode zur "Speicherung" der empfohlenen Versicherung
    def getVersicherungsName():
        versicherungssumme = versicherungssummeMitZusatz()
        if versicherungssumme <= 15000:
            versicherungsName = '"JALC Versicherung"'
        elif versicherungssumme > 15000 and versicherungssumme <= 50000:
            versicherungsName = '"Easy Insurance"'
        elif versicherungssumme > 50000 and versicherungssumme <= 100000:
            versicherungsName = '"Insurance24"'
        else:
            versicherungsName = '"Premium Versicherung"'
        return versicherungsName

    # Herausfinden wohin weitergeleitet werden muss und entsprechende Frage anhängen (unfertig - nicht alle Intents hinzugefügt)
    def gibWeiterleitung():
        dummie = ""
        i = 0
        while (dummie == "" or dummie == "None"):
            if '/contexts/1default_welcome_intent' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Kannst du mir nun bitte noch deinen Namen nennen?"
                break
            if '/contexts/20name_wissen' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Weißt du denn schon genau, was eine Hausratversicherung ist?"
                break
            if '/contexts/30wissenhausratversicherung_nein_wissenhausrat' in str(
                    query_result.get('outputContexts')[i].get('name')):
                dummie = "Verrate mir nun bitte, ob du weißt, was man unter dem Hausrat versteht."
                break
            if '/contexts/311wissenhausrat_nein_beginnen' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Nun sag mir bitte noch, wie du wohnst (z.B. Haus oder Wohnung) und wie groß deine Wohnfläche in m² ist."
                break
            if '/contexts/31wissenhausrat_ja_beginnen' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Nun sag mir bitte noch, wie du wohnst (z.B. Haus oder Wohnung) und wie groß deine Wohnfläche in m² ist."
                break
            if '/contexts/32wissen_ja_beginnen' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Nun sag mir bitte noch, wie du wohnst (z.B. Haus oder Wohnung) und wie groß deine Wohnfläche in m² ist."
                break
            if '/contexts/4groesse_einrichtungswert' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Möchtest du den eben genannten Wert von " + str(rechnerVersicherungsbetrag(
                    getVariableInt('groesse'))) + "€ übernehmen oder auf welchen Betrag soll ich ihn für dich anpassen?"
                break
            if '/contexts/51einrichtungswert_zusatz_normal' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Nun zurück zu meiner ursprünglichen Frage: Möchtest du eine, beide oder keine Zusatzversicherung?"
                break
            if '/contexts/51einrichtungswert_aendern' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Wie hoch soll deine neue Versicherungssumme sein?"
                break
            if '/contexts/51wasempfehlen_einrichtungswert' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Möchtest du den eben genannten Wert von " + str(rechnerVersicherungsbetrag(
                    getVariableInt('groesse'))) + "€ übernehmen oder auf welchen Betrag soll ich ihn für dich anpassen?"
                break
            if '/contexts/51zaendern_zusatz' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Nun zurück zu meiner ursprünglichen Frage: Möchtest du deinen genannten Wert trotzdem beibehalten oder auf welchen Betrag soll ich ihn für dich anpassen?"
                break
            if '/contexts/51zfragebeide' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Möchtest du den Wert von " + re.sub(r'(?<!^)(?=(\d{3})+$)', r'..', str(getVariableInt(
                    'abfrage_versicherungssumme'))) + "€ nun trotzdem beibehalten?"
                break
            if '/contexts/51zfrageueber' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Möchtest du den Wert von " + re.sub(r'(?<!^)(?=(\d{3})+$)', r'..', str(getVariableInt(
                    'abfrage_versicherungssumme'))) + "€ nun trotzdem beibehalten?"
                break
            if '/contexts/51zfrageunter' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Möchtest du den Wert von " + re.sub(r'(?<!^)(?=(\d{3})+$)', r'..', str(getVariableInt(
                    'abfrage_versicherungssumme'))) + "€ nun trotzdem beibehalten?"
                break
            if '/contexts/52ueberunter_aendern' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Zurück zum Thema: Wie hoch soll denn deine neue Versicherungssumme sein?"
                break
            if '/contexts/53aendern_zusatz' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Nun zurück zu meiner ursprünglichen Frage: Möchtest du eine Glasschutz-, Fahrradschutz-, beide oder keine Zusatzversicherung hinzufügen?"
                break
            if '/contexts/54fragebeide_zusatz' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Nun zurück zu meiner ursprünglichen Frage: Möchtest du eine Glasschutz-, Fahrradschutz-, beide oder keine Zusatzversicherung hinzufügen?"
                break
            if '/contexts/54fragefahrrad_zusatz' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Nun zurück zu meiner eigentlichen Frage: Möchtest du eine Glasschutz-, Fahrradschutz-, beide oder keine Zusatzversicherung hinzufügen?"
                break
            if '/contexts/54frageglas_zusatz' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Nun zurück zu meiner eigentlichen Frage: Möchtest du eine Glasschutz-, Fahrradschutz-, beide oder keine Zusatzversicherung hinzufügen?"
                break
            if '/contexts/54fragezusatzkosten_zusatz' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Nun zurück zu meiner eigentlichen Frage: Möchtest du eine Glasschutz-, Fahrradschutz-, beide oder keine Zusatzversicherung hinzufügen?"
                break
            if '/contexts/54ueberunter_beibehalten_zusatz' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Nun zurück zu meiner eigentlichen Frage: Möchtest du eine Glasschutz-, Fahrradschutz-, beide oder keine Zusatzversicherung hinzufügen?"
                break
            if '/contexts/61selbstbehaltfrage_selbstbehalt' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Welche Selbstbeteiligung darf ich für dich eintragen: 0€ oder 150€?"
                break
            if '/contexts/6zusatz_selbstbehalt' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Nun zurück: Welche Selbstbeteiligung darf ich für dich eintragen: 0€ oder 150€?"
                break
            if '/contexts/71zahlungszykluspreisunterschied_zahlunszyklus' in str(
                    query_result.get('outputContexts')[i].get('name')):
                dummie = "Verrate mir bitte nun, in welchem Zyklus du bezahlen möchtest: monatlich, halbjährlich oder einmal pro Jahr."
                break
            if '/contexts/7selbstbehalt_zahlungszyklus' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Verrate mir bitte nun, in welchem Zyklus du bezahlen möchtest: monatlich, halbjährlich oder einmal pro Jahr."
                break
            if '/contexts/8zahlungszyklus_endfragen' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Falls du nun noch eine (fiktive) E-Mail Adresse hinterlässt, meldet sich einer unserer Versicherungsexperten bei dir."
                break
            if '/contexts/91endfragen_nein' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Die Beratung ist nun beendet. Vielen Dank für das angenehme Gespräch!"
                break
            if '/contexts/9endfrage_mehrwissen' in str(query_result.get('outputContexts')[i].get('name')):
                dummie = "Die Beratung ist nun beendet. Vielen Dank für das angenehme Gespräch!"
                break

            i = i + 1
        return str(dummie)

    # Fallback

    if query_result.get('action') == 'input.unknown':
        str_weiterleitung = ""
        str_antwort = ""
        int_fallback = random.randint(0, 2)
        print(int_fallback)
        vorname = ""

        try:
            vorname_help = getVariableStr('vorname.original')
            vorname = ", " + vorname_help.title()
        except Exception:
            print("dort" + vorname)
            vorname = ""
        try:
            str_weiterleitung = str(gibWeiterleitung())
        except Exception:
            str_weiterleitung = "Tut mir leid, ich konnte dich leider nicht verstehen. Wenn du die Beratung von vorne beginnen möchtest, kannst du dies mit der Eingabe “Neustart” tun."

        if (int_fallback == 0):
            str_antwort = "Ich habe dein Anliegen leider nicht verstanden, werde dies jedoch an einen Service Mitarbeiter zur Überprüfung weiterleiten."
        elif (int_fallback == 1):
            str_antwort = "Tut mir leid" + vorname + ". Ich konnte dein Anliegen leider nicht genau verstehen, aber werde dies im Nachhinein an einen menschlichen Kollegen weiterleiten."
        elif (int_fallback == 2):
            str_antwort = "Leider habe ich nicht genau verstanden, was du meinst. Ich werde daher dein Anliegen im Nachgang an einen Mitarbeiter zur Überprüfung weiterleiten."

        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            str_antwort
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            str_weiterleitung
                        ]
                    },

                }
            ],
            "outputContexts":
                setContext()
        }

    # Fragen
    # Frage beste Versicherung
    if query_result.get('action') == 'frage_beste_versicherung':
        dummie = ""
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Das weiß ich leider noch nicht, da es auf deine Rahmenbedingungen ankommt. Am Ende unserer Beratung werde ich dir das genauer sagen können."
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            str(gibWeiterleitung())
                        ]
                    },

                }
            ],
            "outputContexts":
                setContext()
        }

        # Frage Fahrrad mitversichert
    if query_result.get('action') == 'frage_fahrrad_mitversichert':
        dummie = ""
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Das ist eine gute Frage! Du kannst später einen Fahrradschutz dazubuchen, damit wäre dein Fahrrad mitversichert. Die Voraussetzung ist, dass es mit einem Schloss gesichert ist."
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            str(gibWeiterleitung())
                        ]
                    },

                }
            ],
            "outputContexts":
                setContext()
        }

        # Frage Kosten
    if query_result.get('action') == 'frage_kosten':
        dummie = ""
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Gute Frage! Den Preis für die günstigste Hausratversicherung werde ich dir nach der Beratung mitteilen. Dieser hängt vor allem vom Wert deiner Einrichtungsgegenstände ab."
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            str(gibWeiterleitung())
                        ]
                    },

                }
            ],
            "outputContexts":
                setContext()
        }

        # Frage Mitversichert Ja
    if query_result.get('action') == 'frage_mitversichert_ja':
        dummie = ""
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Das wird von allen Versicherungsanbietern in ihrer Hausratversicherung mit abgedeckt."
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            str(gibWeiterleitung())
                        ]
                    },

                }
            ],
            "outputContexts":
                setContext()
        }

        # Frage Mitversichert Nein
    if query_result.get('action') == 'frage_mitversichert_nein':
        dummie = ""
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Dies wird nicht von einer Hausratversicherung abgedeckt."
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            str(gibWeiterleitung())
                        ]
                    },

                }
            ],
            "outputContexts":
                setContext()
        }

        # Frage Warum Hausratversicherung
    if query_result.get('action') == 'frage_warum_hausratversicherung':
        dummie = ""
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Das ist eine gute Frage! Viele Gegenstände in deinem Haushalt haben nicht nur einen persönlichen, sondern auch einen hohen finanziellen Wert. Mit einer abgeschlossenen Hausratversicherung wird dein Hab und Gut im Schadensfall finanziell zum Wiederbeschaffungswert abgesichert. Ohne Versicherung, könnte ein Schadensfall deinen Geldbeutel sehr stark belasten…"
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            str(gibWeiterleitung())
                        ]
                    },

                }
            ],
            "outputContexts":
                setContext()
        }

    # Frage Was ist Hausrat
    if query_result.get('action') == 'frage_was_ist_hausrat':
        dummie = ""
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Zu deinem Hausrat gehören alle Gegenstände, die in deinem Haushalt sind. Stell dir vor, du stellst deine Wohnung oder dein Haus einmal auf den Kopf - alles was jetzt herausfallen kann, gehört zu deinem Hausrat. Dazu zählen unter Anderem deine komplette Einrichtung, Elektrogeräte, Kleidung, Schmuck, Bücher und sogar Vorräte und Bargeld."
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            str(gibWeiterleitung())
                        ]
                    },

                }
            ],
            "outputContexts":
                setContext()
        }

        # Frage Welcher Anbieter
    if query_result.get('action') == 'frage_welche_anbieter':
        dummie = ""
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Ich vergleiche alle Versicherungsanbieter und werde dir abschließend die zu dir am besten passende Versicherung empfehlen."
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            str(gibWeiterleitung())
                        ]
                    },

                }
            ],
            "outputContexts":
                setContext()
        }

    # Frage was gehört zur Wohnfläche
    if query_result.get('action') == 'frage_was_wohnflaeche':
        dummie = ""
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Als Wohnfläche gilt die Grundfläche aller Räume in deiner Wohnung oder deinem Haus. Nicht dazu zählen Flächen von beispielsweise Treppen, Terrasse, Balkonen und Speicher- und Kellerräumen, sofern diese nicht zu Wohn- oder Hobbyzwecken genutzt werden."
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            str(gibWeiterleitung())
                        ]
                    },

                }
            ],
            "outputContexts":
                setContext()
        }

        # Frage Kündigungsfrist
    if query_result.get('action') == 'frage_kuendigungsfrist':
        dummie = ""
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Du kannst bei allen Versicherungsanbietern monatlich kündigen. Falls du deinen Versicherungsbeitrag im Voraus bezahlt hast, bekommst du natürlich die Differenz erstattet. "
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            str(gibWeiterleitung())
                        ]
                    },

                }
            ],
            "outputContexts":
                setContext()
        }

    # Frage für wen arbeitest du
    if query_result.get('action') == 'frage_fuer_wen_arbeitest_du':
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Ich arbeite für keine spezifische Versicherung, sondern bin ein unabhängiger Berater und unterstütze dich bei der Suche nach der besten Hausratversicherung."
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            str(gibWeiterleitung())
                        ]
                    },

                }
            ],
            "outputContexts":
                setContext()
        }

    # Frage Wohnsituation
    if query_result.get('action') == 'frage_wohnsituation':
        print("FRAGE WOHNSITUATION")
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Bei allen Hausratversicherungen kann der Hausrat jeder beliebigen Immobilienart versichert werden - egal ob es sich um eine  Wohnung, ein Einfamilienhaus, ein WG-Zimmer,... handelt."
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            str(gibWeiterleitung())
                        ]
                    },

                }
            ],
            "outputContexts":
                setContext()
        }

    # "Spassfragen"
    # Intent Frage Wer ist Kanzler?
    if query_result.get('action') == 'frage_wer_ist_kanzler':
        dummie = ""
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Momentan ist Olaf Scholz der Bundeskanzler von Deutschland."
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            str(gibWeiterleitung())
                        ]
                    },

                }
            ],
            "outputContexts":
                setContext()
        }

    # Intent Frage Wer hat dich programmiert?
    if query_result.get('action') == 'frage_wer_hat_programmiert':
        dummie = ""
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Ich wurde vom Institut IISM / KSRI erschaffen und bin hier um für dich die perfekte Hausratversicherung zu finden. "
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            str(gibWeiterleitung())
                        ]
                    },

                }
            ],
            "outputContexts":
                setContext()
        }
    # Intent Witz

    if query_result.get('action') == 'frage_sag_witz':
        int_witz_random = random.randint(0, 2)
        str_witz = ""
        if (int_witz_random == 0):
            str_witz = '"Was machen Pilze auf einer Pizza?" - "Als Belag funghieren"'
        elif (int_witz_random == 1):
            str_witz = '"Aber der Kaffee ist doch kalt Herr Kellner." - "Gut, dass Sie das sagen. Eiskaffee kostet nämlich einen Euro mehr."'
        else:
            str_witz = '"Welcher Ring ist nicht rund?" - "Der Hering"'

        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            str_witz
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            str(gibWeiterleitung())
                        ]
                    },

                }
            ],
            "outputContexts":
                setContext()
        }

    # Frage Wie alt bist du?
    if query_result.get('action') == 'frage_wie_alt_bist_du':
        dummie = ""
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Ich bin alt genug, um dich beim Finden der passenden Hausratversicherung zu unterstützen. "
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            str(gibWeiterleitung())
                        ]
                    },

                }
            ],
            "outputContexts":
                setContext()
        }

    # Frage Wie geht es dir?
    if query_result.get('action') == 'frage_wie_geht_es_dir':
        dummie = ""
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Mir geht es gut, danke der Nachfrage!"
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            str(gibWeiterleitung())
                        ]
                    },

                }
            ],
            "outputContexts":
                setContext()
        }

    # Frage Was kannst du?
    if query_result.get('action') == 'frage_was_kannst_du':
        dummie = ""
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Ich bin ein digitaler Versicherungsberater und unterstütze dich dabei, eine passende Hausratversicherung zu finden. Ich bin kein Mensch, daher kann es sein, dass ich auf manche Fragen keine perfekte Antwort parat habe."
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            str(gibWeiterleitung())
                        ]
                    },

                }
            ],
            "outputContexts":
                setContext()
        }

        # Frage Wie groß bist du?
    if query_result.get('action') == 'frage_wie_gross_bist_du':
        dummie = ""
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Ich bin groß genug, um dich beim Finden der passenden Hausratversicherung zu unterstützen."
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            str(gibWeiterleitung())
                        ]
                    },

                }
            ],
            "outputContexts":
                setContext()
        }

    # Intent Welcome - inklusive zurücksetzen des "Variablen" Kontext
    if query_result.get('action') == 'input.welcome':
        # Start Test
        dummie = ""
        # Ende Test
        i = 0
        try:
            while (dummie == "" or dummie == "None"):
                if '/contexts/variable' in str(query_result.get('outputContexts')[i].get('name')):
                    dummie = str(query_result.get('outputContexts')[i].get('name'))
                    break
                i = i + 1
        except Exception:
            print("Neustart")
            return {
                "fulfillmentText": "Hallo, mein Name ist Hugo und ich bin dein virtueller Berater. Und wie heißt du?"}

        return {
            "fulfillmentText": "Hallo, mein Name ist Hugo und ich bin dein virtueller Berater. Und wie heißt du?",
            "outputContexts": [
                {
                    "name": dummie,
                    "lifespanCount": 0
                }
            ]
        }

    # Intent: name_wissen, Abfrage von vorname
    if query_result.get('action') == 'get.name':
        i = 0
        # time.sleep(1)
        vorname = getVariableStr("vorname.original")
        vorname = vorname.title()

        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Schön dich kennen zu lernen, " + vorname + ". Ich bin hier, um dir dabei zu helfen, die beste Hausratversicherung für dich unter allen Anbietern zu finden."
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            "Weißt du denn schon genau, was eine Hausratversicherung ist?"
                        ]
                    },

                }
            ],
        }

    # Intent: 3.0wissenHausratVersicherung_nein_wissenHausrat
    if query_result.get('action') == '3.0wissenHausratVersicherung_nein_wissenHausrat':
        # time.sleep(2.2)
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Die Hausratversicherung versichert deinen Hausrat zum Wiederbeschaffungswert und kommt für Schäden durch Feuer, Einbruchdiebstahl, Vandalismus, Leitungswasser, Sturm und Hagel auf. "
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            "Weißt du denn auch, was man unter dem Hausrat versteht?"
                        ]
                    },

                }
            ],
        }

    # Intent: 3.1.1wissenHausrat_nein_beginnen
    if query_result.get('action') == '3.1.1wissenHausrat_nein_beginnen':
        # time.sleep(1.7)
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Stell dir vor, du stellst deine Wohnung oder dein Haus einmal auf den Kopf - alles was jetzt herausfallen kann, gehört zu deinem Hausrat."
                        ]
                    },
                },
                {
                    "text": {
                        "text": [
                            "Um nun deine personalisierte Hausratversicherung zu finden, müsste ich noch einiges wissen. Zuerst verrate mir bitte, wie du wohnst (z.B. Haus oder Wohnung) und wie groß deine Wohnfläche in m² ist."
                        ]
                    },
                }
            ],
        }

    # Intent: 3.1wissenHausrat_ja_beginnen
    if query_result.get('action') == '3.1wissenHausrat_ja_beginnen':
        # time.sleep(1.1)
        return {
            "fulfillmentText":
                "Prima, dann kennst du dich ja aus! \nUm nun deine personalisierte Hausratversicherung zu finden, müsste ich noch einiges wissen. Zuerst verrate mir bitte, wie du wohnst (z.B. Haus oder Wohnung) und wie groß deine Wohnfläche in m² ist."
        }

        # Intent: wissen_ja_beginnen
    if query_result.get('action') == '3.2wissen_ja_beginnen':
        # time.sleep(1.0)
        return {
            "fulfillmentText":
                "Prima, dann kennst du dich ja aus! \nUm nun deine personalisierte Hausratversicherung zu finden, müsste ich noch einiges wissen. Zuerst verrate mir bitte, wie du wohnst (z.B. Haus oder Wohnung) und wie groß deine Wohnfläche in m² ist."
        }

        # Intent: 4groesse_einrichtungswert
    if query_result.get('action') == '4groesse_einrichtungswert':
        # time.sleep(2.0)
        groesse = 0
        groesse = getVariableInt('groesse')
        str_versicherungsbetrag_einrichtungswert = rechnerVersicherungsbetrag(groesse)

        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            str(groesse) + " m² sind notiert! Lass uns nun gemeinsam den Wert deines Hausrats bestimmen. Der durchschnittliche Versicherungsbetrag liegt bei 650€ pro m². Damit wäre dein gesamter Hausrat bis zu einer Höhe von " + str_versicherungsbetrag_einrichtungswert + "€ versichert. "
                        ]
                    },
                },
                {
                    "text": {
                        "text": [
                            "Falls du Hilfe bei der Einschätzung deiner Versicherungssumme brauchst, schreib` gerne \"Hilfe\". Ansonsten, möchtest du den Wert von " + str_versicherungsbetrag_einrichtungswert + "€ übernehmen oder auf welche Summe soll ich ihn für dich anpassen?"
                        ]
                    },
                }
            ],
        }

    # Intent 5.1wasEmpfehlen_einrichtungswert
    if query_result.get('action') == 'wasEmpfehlen_einrichtungswert':
        # time.sleep(2)
        groesse = 0
        groesse = getVariableInt('groesse')
        str_versicherungsbetrag_einrichtungswert = rechnerVersicherungsbetrag(groesse)

        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Ich helfe dir gerne bei der Einschätzung. Es ist sinnvoll, die Versicherungssumme anzupassen, wenn der Wert deiner Einrichtungsgegenstände stark von der für dich berechneten Summe von " + str_versicherungsbetrag_einrichtungswert + "€ abweicht. Korrigiere den Wert nach oben, falls du z. B. sehr teure Möbel, Sammlungen oder hochwertigen Schmuck besitzt - ändere den Wert nach unten ab, falls du eher günstige Möbel und kaum Wertgegenstände besitzt."
                        ]
                    },
                },
                {
                    "text": {
                        "text": [
                            "Möchtest du nun den Wert von " + str_versicherungsbetrag_einrichtungswert + "€ übernehmen oder auf welche Summe soll ich ihn für dich anpassen?"
                        ]
                    },
                }
            ],
        }

    # Fallback- Intent: groesse_einrichtungswert, Abfrage von groesse
    if query_result.get('action') == '4groesse_einrichtungswert.4groesse_einrichtungswert-fallback':
        # time.sleep(1.5)
        groesse = 0
        groesse = getVariableInt('groesse')
        str_versicherungsbetrag_einrichtungswert = rechnerVersicherungsbetrag(groesse)

        return {
            "fulfillmentText":
                "Falls du noch beraten werden willst, frag gerne nach. Anonsten soll ich den Wert von " + str_versicherungsbetrag_einrichtungswert + "€ für dich übernehmen oder auf welche Summe kann ich ihn anpassen?"
        }

    # Intent: einrichtungswert_zusatz_normal
    if query_result.get('action') == 'get.einrichtungswert_normal':
        # time.sleep(1.2)
        return {

            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "In Ordnung, die Summe trage ich gerne ein. \nUm deinen Versicherungsschutz zu erweitern, kannst du noch die Zusatzversicherungen Fahrradschutz oder Glasschutz dazubuchen."
                        ]
                    },
                },
                {
                    "text": {
                        "text": [
                            "Möchtest du eine, oder sogar beide, oder keine Zusatzversicherung hinzufügen?\nFalls du dazu noch Fragen hast, frag mich einfach."
                        ]
                    },
                }
            ],
        }

    # Intent: einrichtungswert_aendern
    if query_result.get('action') == 'get.einrichtungswert_aendern':
        # time.sleep(1.1)
        return {
            "fulfillmentText":
                "Wie hoch soll deine neue Versicherungssumme sein?"
        }

    # Intent: zaendern_zusatz
    if query_result.get('action') == 'zaendern_zusatz':
        # Aendern der Vairable versicherungsbetrag_einrichtungswert
        vorname = getVariableStr('vorname.original').title()
        groesse = 0
        groesse = getVariableInt('groesse')
        versicherungsbetrag_einrichtungswert_help = groesse * 650
        versicherungsbetrag_einrichtungswert = 0
        versicherungsbetrag_einrichtungswert = int(getVariableInt('abfrage_versicherungssumme'))
        # time.sleep(1.9)

        if versicherungsbetrag_einrichtungswert == 0:
            return {
                "fulfillmentText":
                    "Wie hoch soll deine neue Versicherungssumme sein?"
            }

        elif versicherungsbetrag_einrichtungswert > versicherungsbetrag_einrichtungswert_help:
            help = versicherungsbetrag_einrichtungswert - versicherungsbetrag_einrichtungswert_help
            if (help / versicherungsbetrag_einrichtungswert_help) > 0.3:
                return {
                    "fulfillmentText":
                        "Vorsicht " + vorname + ", du weichst stark von der empfohlenen Versicherungssumme ab. Es könnte sein, dass du damit überversichert bist. \nMöchtest du den Wert von " + re.sub(
                            r'(?<!^)(?=(\d{3})+$)', r'..',
                            str(versicherungsbetrag_einrichtungswert)) + "€ trotzdem beibehalten?"
                }

        elif versicherungsbetrag_einrichtungswert <= versicherungsbetrag_einrichtungswert_help:
            help = versicherungsbetrag_einrichtungswert_help - versicherungsbetrag_einrichtungswert
            if (help / versicherungsbetrag_einrichtungswert_help) > 0.3:
                return {
                    "fulfillmentText":
                        "Vorsicht " + vorname + ", du weichst stark von der empfohlenen Versicherungssumme ab. Es könnte sein, dass du damit unterversichert bist. \nMöchtest du den Wert von " + re.sub(
                            r'(?<!^)(?=(\d{3})+$)', r'..',
                            str(versicherungsbetrag_einrichtungswert)) + "€ trotzdem beibehalten?"
                }

        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "In Ordnung, die Summe trage ich gerne ein. \nUm deinen Versicherungsschutz zu erweitern, kannst du noch die Zusatzversicherungen Fahrradschutz oder Glasschutz dazubuchen."
                        ]
                    },
                },
                {
                    "text": {
                        "text": [
                            "Möchtest du eine, oder sogar beide, oder keine Zusatzversicherung hinzufügen?"
                        ]
                    },
                }
            ],
        }

    # Intent um nach Abfrage wegen großer Abweichung Versicherungssumme zu ändern
    if query_result.get('action') == 'ueberUnter_aendern':
        # time.sleep(1)
        return {
            "fulfillmentText":
                "Okay, wie hoch soll dann deine neue Versicherungssumme sein?"
        }

    # Intent zur Anpassung der Versicherungssumme nach Änderungsintent
    if query_result.get('action') == 'aendern_zusatz':
        # time.sleep(1.2)

        return {

            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "In Ordnung, die Summe trage ich gerne ein. \nUm deinen Versicherungsschutz zu erweitern, kannst du noch die Zusatzversicherungen Fahrradschutz oder Glasschutz dazubuchen."
                        ]
                    },
                },
                {
                    "text": {
                        "text": [
                            "Möchtest du eine, sogar beide oder keine Zusatzversicherung hinzufügen?"
                        ]
                    },
                }
            ],
        }

    # Intent zum Beibehalten der angepassten Versicherungssumme
    if query_result.get('action') == 'ueberUnter_beibehalten_zusatz':
        # time.sleep(1.5)

        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "In Ordnung, die Summe trage ich gerne ein. \nUm deinen Versicherungsschutz zu erweitern, kannst du noch die Zusatzversicherungen Fahrradschutz oder Glasschutz dazubuchen."
                        ]
                    },
                },
                {
                    "text": {
                        "text": [
                            "Möchtest du eine, sogar beide oder keine Zusatzversicherung hinzufügen?"
                        ]
                    },
                }
            ],
        }

    # Intent um Frage zu Fahrradschutz zu beantworten
    if query_result.get('action') == 'frageFahrrad_zusatz':
        # time.sleep(2.2)
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Mit dem Fahrradschutz sicherst du dein Fahrrad bei Diebstahl finanziell ab. Versichert sind alle Fahrräder deines Haushalts, vorausgesetzt, sie sind mit einem Schloss gesichert und stehen an einem Ort, der im Versicherungsschein aufgeführt ist, z.B. Garage oder Keller."
                        ]
                    },
                },
                {
                    "text": {
                        "text": [
                            "Sage mir nun bitte, welche Zusatzversicherung du brauchst: Glasschutz, Fahrradschutz, beide oder keine."
                        ]
                    },
                }
            ],
        }

    # Intent um Frage zu Glasschutzversicherung zu beantworten
    if query_result.get('action') == 'frageGlas_zusatz':
        # time.sleep(2.2)
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Im Basis-Tarif einer Hausratversicherung sind Glasschäden nicht abgedeckt. Wenn du also viel Glasmobiliar oder großflächige Fenster besitzt, lohnt es sich, den Glasschutz dazu zu buchen. Damit wären im Schadensfall Scheiben, Spiegel, Möbel, Duschkabinen oder die Glasscheiben von Aquarien, Terrarien und Wintergärten finanziell abgesichert."
                        ]
                    },
                },
                {
                    "text": {
                        "text": [
                            "Sage mir nun bitte, welche Zusatzversicherung du brauchst: Glasschutz, Fahrradschutz, beide oder keine."
                        ]
                    },
                }
            ],
        }

    # Intent um Frage zu beiden zu beantworten
    if query_result.get('action') == 'frageBeide_zusatz':
        # time.sleep(2.2)
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "In den normalen Basistarifen der Versicherungsanbieter sind Dinge wie dein Fahrrad oder Gegenstände aus Glas nicht mitversichert."
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            "Sag mir nun am besten, welche Zusatzversicherung du gerne hättest: Glasschutz, Fahrradschutz, beide oder keine."
                        ]
                    },

                }
            ],
        }

    # Intent zusatz_selbstbehalt, abrufen der Variable zusatz
    if query_result.get('action') == 'get.zusatz':
        versicherungssumme = versicherungssummeMitZusatz()
        zusatz = getVariableStr('zusatz').title()
        selbst0 = str(int(versicherungssumme / 800))
        selbst150 = str(int(versicherungssumme / 920))
        print(zusatz)

        if zusatz == "Keine":
            return {
                "fulfillmentText":
                    "Gut, dann bleiben wir beim Basistarif.\nKommt dein Hausrat zu Schaden, kannst du für einen Teil des Schadens selbst aufkommen. Wählst du eine Selbstbeteiligung von 0€, dann beträgt dein jährlicher Versicherungsbeitrag " + selbst0 + "€, bei 150€ Selbstbeteiligung wären es " + selbst150 + "€ pro Jahr. \n\nWie hoch soll deine Selbstbeteiligung sein?"
            }

        if zusatz == "Fahrrad":
            return {
                "fulfillmentText":
                    "Gut, dann buchen wir die Fahrradschutzversicherung hinzu.\nKommt dein Hausrat zu Schaden, kannst du für einen Teil des Schadens selbst aufkommen. Wählst du eine Selbstbeteiligung von 0€, dann beträgt dein jährlicher Versicherungsbeitrag " + selbst0 + "€, bei 150€ Selbstbeteiligung wären es " + selbst150 + "€ pro Jahr. \n\nWie hoch soll deine Selbstbeteiligung sein?"
            }

        if zusatz == "Glas":
            return {
                "fulfillmentText":
                    "Gut, dann buchen wir die Glasschutzversicherung hinzu. \nKommt dein Hausrat zu Schaden, kannst du für einen Teil des Schadens selbst aufkommen. Wählst du eine Selbstbeteiligung von 0€, dann beträgt dein jährlicher Versicherungsbeitrag " + selbst0 + "€, bei 150€ Selbstbeteiligung wären es " + selbst150 + "€ pro Jahr. \n\nWie hoch soll deine Selbstbeteiligung sein?"
            }

        if zusatz == "Beide":
            return {
                "fulfillmentText":
                    "Gut, dann buchen wir die Glas- und Fahrradschutzversicherung hinzu.\nKommt dein Hausrat zu Schaden, kannst du für einen Teil des Schadens selbst aufkommen. Wählst du eine Selbstbeteiligung von 0€, dann beträgt dein jährlicher Versicherungsbeitrag " + selbst0 + "€, bei 150€ Selbstbeteiligung wären es " + selbst150 + "€ pro Jahr. \n\nWie hoch soll deine Selbstbeteiligung sein?"
            }

    # Fallback
    if query_result.get('action') == '6zusatz_selbstbehalt.6zusatz_selbstbehalt-custom':
        # time.sleep(1.2)

        versicherungssumme = versicherungssummeMitZusatz()
        zusatz = getVariableStr('zusatz').title()
        selbst0 = str(int(versicherungssumme / 800))
        selbst150 = str(int(versicherungssumme / 920))

        return {
            "fulfillmentText":
                "Klar! Bei einer Selbstbeteiligung von 0€ liegt dein Versicherungsbeitrag bei " + selbst0 + "€ pro Jahr und bei einer Selbstbeteiligung von 150€ bei " + selbst150 + "€ pro Jahr. \n\nWie hoch soll deine Selbstbeteiligung sein?"
        }

    # Intent selbstbehalt_zahlungszyklus, abrufen der Variable selbst
    if query_result.get('action') == 'get.selbstbehalt':
        return {
            "fulfillmentText":
                "Okay, zu guter Letzt bräuchte ich noch eine Angabe, ob du monatlich, halbjährlich oder jährlich bezahlen möchtest. Wie möchtest du am liebsten zahlen?"
        }

    # Erstellen der Übersicht in Intent Übersicht
    if query_result.get('action') == 'get.uebersicht':
        # Entscheidung, welcher Versicherungsname
        versicherungsName = getVersicherungsName()
        zahlungszyklus = getVariableStr('zahlungszyklus')
        selbstbeteiligung = getVariableStr('selbst')
        zusatz = getVariableStr('zusatz').title()
        versicherungssumme = versicherungssummeMitZusatz()
        vorname = getVariableStr('vorname.original').title()

        # time.sleep(1.5)

        endwert = 0
        selbstbeteiligung = str(selbstbeteiligung)

        if selbstbeteiligung == "0":
            endwert = (versicherungssumme / 800)
        elif selbstbeteiligung == "150":
            endwert = (versicherungssumme / 920)

        textBlock_zusatz = ""

        if zusatz == "Keine":
            textBlock_zusatz = "Neben dem Basistarif hast du keine Zusatzversicherungen ausgewählt."
        if zusatz == "Fahrrad":
            textBlock_zusatz = "Zusätzlich zum Basistarif hast du noch die Fahrradschutzversicherung ausgewählt."
        if zusatz == "Glas":
            textBlock_zusatz = "Zusätzlich zum Basistarif hast du noch die Glasschutzversicherung ausgewählt."
        if zusatz == "Beide":
            textBlock_zusatz = "Zusätzlich zum Basistarif hast du noch die Glas- und Fahrradschutzversicherung ausgewählt."
        str_endwert = str(endwert).replace('.', ',')

        if zahlungszyklus == "monatlich":
            endwert = round((endwert / 12), 2)
            str_endwert = str(endwert).replace('.', ',')
            i = 0
            while (i < 10):
                if str(',0' + str(i)) in str_endwert:
                    break
                i = i + 1
            if i == 10:
                str_endwert = str_endwert.replace(',0', '')
            if "," in str_endwert and str_endwert[-3] != ",":
                str_endwert = str_endwert + "0"
            if "," in str_endwert and str_endwert[-3] != ",":
                str_endwert = str_endwert + "0"

            return {

                "fulfillmentMessages": [
                    {
                        "text": {
                            "text": [
                                "Vielen Dank für das angenehme Gespräch, " + vorname + ". " + textBlock_zusatz + " Unter allen Versicherungsanbietern habe ich bei der " + versicherungsName + " die am besten zu dir passende Hausratversicherung gefunden. Diese würde dich " + str_endwert + "€/Monat kosten."
                            ]
                        },

                    },
                    {
                        "text": {
                            "text": [
                                "Wenn du zum Abschluss noch eine (fiktive) Email-Adresse hinterlässt, meldet sich unser Versicherungsexperte in den nächsten Tagen mit weiteren Infos und dem finalen Angebot bei dir."
                            ]
                        },

                    }
                ],
            }


        elif zahlungszyklus == "halbjährlich":
            endwert = round((endwert / 2), 2)
            str_endwert = str(endwert).replace('.', ',')
            i = 0
            while (i < 10):
                if str(',0' + str(i)) in str_endwert:
                    break
                i = i + 1
            if i == 10:
                str_endwert = str_endwert.replace(',0', '')
            if "," in str_endwert and str_endwert[-3] != ",":
                str_endwert = str_endwert + "0"
            if "," in str_endwert and str_endwert[-3] != ",":
                str_endwert = str_endwert + "0"
            return {
                "fulfillmentMessages": [
                    {
                        "text": {
                            "text": [
                                "Vielen Dank für das angenehme Gespräch, " + vorname + ". " + textBlock_zusatz + " Unter allen Versicherungsanbietern habe ich bei der " + versicherungsName + " die am besten zu dir passende Hausratversicherung gefunden. Diese würde dich " + str_endwert + "€ zwei mal im Jahr kosten."
                            ]
                        },

                    },
                    {
                        "text": {
                            "text": [
                                "Wenn du zum Abschluss noch eine (fiktive) Email-Adresse hinterlässt, meldet sich unser Versicherungsexperte in den nächsten Tagen mit weiteren Infos und dem finalen Angebot bei dir."
                            ]
                        },

                    }
                ],
            }

        elif zahlungszyklus == "jährlich":
            endwert = round(endwert, 2)
            str_endwert = str(endwert).replace('.', ',')
            i = 0
            while (i < 10):
                if str(',0' + str(i)) in str_endwert:
                    break
                i = i + 1
            if i == 10:
                str_endwert = str_endwert.replace(',0', '')
            if "," in str_endwert and str_endwert[-3] != ",":
                str_endwert = str_endwert + "0"
            if "," in str_endwert and str_endwert[-3] != ",":
                str_endwert = str_endwert + "0"
            return {
                "fulfillmentMessages": [
                    {
                        "text": {
                            "text": [
                                "Vielen Dank für das angenehme Gespräch, " + vorname + ". " + textBlock_zusatz + " Unter allen Versicherungsanbietern habe ich bei der " + versicherungsName + " die am besten zu dir passende Hausratversicherung gefunden. Diese würde dich " + str_endwert + "€/Jahr kosten."
                            ]
                        },

                    },
                    {
                        "text": {
                            "text": [
                                "Wenn du zum Abschluss noch eine (fiktive) Email-Adresse hinterlässt, meldet sich unser Versicherungsexperte in den nächsten Tagen mit weiteren Infos und dem finalen Angebot bei dir."
                            ]
                        },

                    }
                ],
            }

    # Intent 9.1endFragen_nein
    if query_result.get('action') == 'get.9.1endFragen_nein':
        # time.sleep(1.5)
        vorname = getVariableStr('vorname.original').title()
        versicherungsName = getVersicherungsName()
        versicherungsName = versicherungsName.lower().replace(" ", "").replace('"', "")
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Alles klar. Du kannst gerne unter der Website www." + versicherungsName + ".de mehr erfahren. Ich wünsche Dir noch einen schönen Tag " + vorname + "."
                        ]
                    }

                }
            ],
        }
    # Intent endfrage_mehrwissen
    if query_result.get('action') == 'endfrage_mehrwissen':
        # time.sleep(1)
        return {
            "fulfillmentText":
                "Ok, die E-Mail Adresse ist notiert. Dein persönlicher Versicherungsberater wird sich schnellstsmöglich bei dir melden. Ich wünsche dir noch einen schönen Tag."
        }

        # Intent schickMail
    # if query_result.get('action') == 'schickMail':

    # userEmail = ""
    # i = 0
    # time.sleep(1)
    # while(userEmail == "" or userEmail == "None"):
    # try:
    #  userEmail = str(query_result.get('outputContexts')[i].get('parameters').get('email'))
    #  i = i + 1
    # except Exception:
    #   print("normaler Fehler Aufruf Email")

    # ue_zahlungszyklus = ''
    # if zahlungszyklus == "monatlich":
    #  ue_zahlungszyklus = " pro Monat"

    # if zahlungszyklus == "halbjährlich":
    #   ue_zahlungszyklus = " halbjährlich"
    # if zahlungszyklus == "jährlich":
    #   ue_zahlungszyklus = " pro jahr"

    # fromx = 'teamprojektcamail@gmail.com'
    # to  = userEmail
    # text = 'Liebe:r ' + vorname + ', \n \nGesamtkosten: ' + str(endwert) + '€' + ue_zahlungszyklus + '\nZusatzversicherungen: ' + zusatz + '\nVersicherungssumme: ' + str(versicherungsbetrag_einrichtungswert) + '€\nWohnfläche: ' + str(groesse) + 'm²' + '\n\n Viele Grüße\nDein Teamprojekt Team'
    # msg = MIMEText(text)
    # msg['Subject'] = 'Übersicht'
    #  msg['From'] = fromx
    # msg['To'] = to

    # server = smtplib.SMTP('smtp.gmail.com:587')
    #  server.starttls()
    # server.ehlo()
    # server.login('teamprojektcamail@gmail.com', 'TeamprojektCA21.')
    # server.sendmail(fromx, to, msg.as_string())

    #  server.quit()

    # return{
    #   "fulfillmentText": "E-Mail wurde erfolgreich versendet"
    #  }

    # Intent Frage Hausratversicherung beginnen
    if query_result.get('action') == 'frageHausratversicherung_beginnen':
        # time.sleep(2.5)
        return {

            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Mit einer Hausratversicherung wird dein Hab und Gut zum Wiederbeschaffungswert abgesichert, beschädigte Gegenstände kannst du dir danach also einfach neu kaufen. Die Versicherung greift bei aufgekommenen Schäden durch Feuer, Einbruchdiebstahl, Vandalismus, Leitungswasser, Sturm und Hagel."
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            "Hast du noch weitere Fragen, bei denen ich dir helfen kann?"
                        ]
                    },

                }
            ],
        }

    if query_result.get('action') == 'frageWarumHausrat_beginnen':
        # time.sleep(2.5)
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Das ist eine gute Frage! Viele Gegenstände in deinem Haushalt haben nicht nur einen persönlichen, sondern auch einen hohen finanziellen Wert. Mit einer abgeschlossenen Hausratversicherung wird dein Hab und Gut im Schadensfall finanziell zum Wiederbeschaffungswert abgesichert. Ohne Versicherung, könnte ein Schadensfall deinen Geldbeutel sehr stark belasten…"
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            "Hast du noch weitere Fragen, bei denen ich dir helfen kann?"
                        ]
                    },

                }
            ],
        }

    if query_result.get('action') == 'frageWasGehoertWohnflaeche_beginnen':
        # time.sleep(2.5)
        return {

            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Das beantworte ich dir gerne. Als Wohnfläche gilt die Grundfläche aller Räume in deiner Wohnung oder deinem Haus. Nicht dazu zählen Flächen von beispielsweise Treppen, Terrasse, Balkonen und Speicher- und Kellerräumen, sofern diese nicht zu Wohn- oder Hobbyzwecken genutzt werden."
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            "Hast du noch weitere Fragen, bei denen ich dir helfen kann?"
                        ]
                    },

                }
            ],

        }

    if query_result.get('action') == 'frageWasVerstehtHausrat_beginnen':
        # time.sleep(2.5)
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Zu deinem Hausrat gehören alle Gegenstände, die in deinem Haushalt sind. Stell dir vor, du stellst deine Wohnung oder dein Haus einmal auf den Kopf - alles was jetzt herausfallen kann, gehört zu deinem Hausrat. Dazu zählen unter Anderem deine komplette Einrichtung, Elektrogeräte, Kleidung, Schmuck, Bücher und sogar Vorräte und Bargeld."
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            "Hast du noch weitere Fragen, bei denen ich dir helfen kann?"
                        ]
                    },

                }
            ],
        }

    # Intent: zfrageUeber, Frage was ist Überversicherung
    if query_result.get('action') == 'zfrageUeber':
        # time.sleep(2.5)
        versicherungsbetrag_einrichtungswert = getVariableInt('abfrage_versicherungssumme')

        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Eine Überversicherung liegt vor, wenn du den Wert deines Hausrat höher einschätzt, als er eigentlich ist. Dadurch wäre dein Versicherungsbeitrag höher als nötig."
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            "Möchtest du den Wert von " + re.sub(r'(?<!^)(?=(\d{3})+$)', r'..',
                                                                 str(versicherungsbetrag_einrichtungswert)) + "€ trotzdem beibehalten?"
                        ]
                    },
                }
            ],
        }

    # Intent: zfrageUnter, Frage was ist Unterversicherung
    if query_result.get('action') == 'zfrageUnter':
        # time.sleep(2.5)
        versicherungsbetrag_einrichtungswert = getVariableInt('abfrage_versicherungssumme')
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Eine Unterversicherung liegt vor, wenn du den Wert deines Hausrat niedriger einschätzt, als er eigentlich ist. Damit gehst du das Risiko ein, dass dein Schaden nicht vollständig erstattet wird."
                        ]
                    },
                },
                {
                    "text": {
                        "text": [
                            "Möchtest du den Wert von " + re.sub(r'(?<!^)(?=(\d{3})+$)', r'..',
                                                                 str(versicherungsbetrag_einrichtungswert)) + "€ trotzdem beibehalten?"
                        ]
                    },
                }
            ],
        }

    # Intent: zfrageBeide, Frage was ist Über-/Unterversicherung
    if query_result.get('action') == 'zfrageBeide':
        # time.sleep(2.5)
        versicherungsbetrag_einrichtungswert = getVariableInt('abfrage_versicherungssumme')
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Also eine Überversicherung liegt vor, wenn du den Wert deines Hausrat höher einschätzt, als er eigentlich ist. Dadurch wäre dein Versicherungsbeitrag höher als nötig.\nEine Unterversicherung liegt vor, wenn du den Wert deines Hausrat niedriger einschätzt, als er eigentlich ist. Damit gehst du das Risiko ein, dass dein Schaden nicht vollständig erstattet wird."
                        ]
                    },

                },
                {
                    "text": {
                        "text": [
                            "Möchtest du den Wert von " + re.sub(r'(?<!^)(?=(\d{3})+$)', r'..',
                                                                 str(versicherungsbetrag_einrichtungswert)) + "€ trotzdem beibehalten?"
                        ]
                    },

                }
            ],
        }

    # Intent DankeDirAuch
    if query_result.get('action') == 'DankeDirAuch':
        # time.sleep(1)
        vorname = getVariableStr('vorname.original').title()

        return {
            "fulfillmentText": "Bis bald, " + vorname + "."
        }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)  # This line is required to run Flask on repl.it