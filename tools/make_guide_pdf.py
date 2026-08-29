#!/usr/bin/env python3
"""
Générateur du Guide de Découverte et d'Utilisation ShockDesk (PDF 9 pages).
Utilise fpdf2 et la police DejaVuSans pour un rendu typographique propre et complet en UTF-8.
"""

import os
import sys
from fpdf import FPDF
from fpdf.enums import XPos, YPos

# Définition des chemins
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
OUTPUT_PDF = os.path.join(DOCS_DIR, "decouverte-shockdesk.pdf")

DEJAVU_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DEJAVU_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


class ShockDeskPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=False)
        self.set_margins(left=15, top=15, right=15)
        
        # Ajout des polices DejaVu
        if os.path.exists(DEJAVU_REGULAR) and os.path.exists(DEJAVU_BOLD):
            self.add_font("DejaVu", "", DEJAVU_REGULAR)
            self.add_font("DejaVu", "B", DEJAVU_BOLD)
            self.font_main = "DejaVu"
        else:
            self.font_main = "Helvetica"
            
        if os.path.exists(DEJAVU_MONO):
            self.add_font("DejaVuMono", "", DEJAVU_MONO)
            self.font_mono = "DejaVuMono"
        else:
            self.font_mono = "Courier"

    def header(self):
        self.set_font(self.font_main, "B", 8)
        self.set_text_color(100, 116, 139) # slate 500
        self.cell(0, 5, "SHOCKDESK — Manuel de Référence & Guide du Desk", new_x=XPos.RIGHT, new_y=YPos.TOP, align="L")
        self.cell(0, 5, "https://shockdesk.onrender.com", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
        self.set_draw_color(226, 232, 240)
        self.line(15, 21, 195, 21)
        self.ln(4)

    def footer(self):
        self.set_y(-14)
        self.set_font(self.font_main, "", 8)
        self.set_text_color(148, 163, 184) # slate 400
        self.set_draw_color(226, 232, 240)
        self.line(15, 283, 195, 283)
        self.cell(0, 8, "ShockDesk • Plateforme de Recherche Macro & Backtest Quant", new_x=XPos.RIGHT, new_y=YPos.TOP, align="L")
        self.cell(0, 8, f"Page {self.page_no()} / 9", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

    def page_title(self, num, title, subtitle=None):
        self.set_y(24)
        self.set_font(self.font_main, "B", 14)
        self.set_text_color(15, 23, 42) # slate 900
        self.cell(0, 7, f"{num}. {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
        if subtitle:
            self.set_font(self.font_main, "", 9)
            self.set_text_color(71, 85, 105) # slate 600
            self.cell(0, 5, subtitle, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
        self.ln(2)

    def section_header(self, title):
        self.set_font(self.font_main, "B", 10)
        self.set_text_color(30, 41, 59) # slate 800
        self.set_fill_color(241, 245, 249) # slate 100
        self.cell(0, 6, f"  {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L", fill=True)
        self.ln(1.5)

    def card_box(self, x, y, w, h, bg_color=(248, 250, 252), border_color=(203, 213, 225)):
        self.set_fill_color(*bg_color)
        self.set_draw_color(*border_color)
        self.rect(x, y, w, h, style="FD")


def generate_pdf():
    os.makedirs(DOCS_DIR, exist_ok=True)
    pdf = ShockDeskPDF()

    # =========================================================================
    # PAGE 1 : BIENVENUE & L'ANALOGIE DU SIMULATEUR DE VOL
    # =========================================================================
    pdf.add_page()
    
    # En-tête spécial page 1
    pdf.set_y(24)
    pdf.set_fill_color(15, 23, 42) # Dark Slate Header
    pdf.rect(15, 24, 180, 24, style="F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(pdf.font_main, "B", 15)
    pdf.set_xy(20, 27)
    pdf.cell(170, 7, "SHOCKDESK — GUIDE DE DÉCOUVERTE DU DESK", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font(pdf.font_main, "", 9)
    pdf.set_xy(20, 34)
    pdf.set_text_color(203, 213, 225)
    pdf.cell(170, 5, "De la thèse macroscopique au trade testé : Maîtriser le risque sans illusion", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_y(52)
    pdf.section_header("1. L'Analogie du Simulateur de Vol : Pourquoi ShockDesk ?")
    
    pdf.set_font(pdf.font_main, "", 9)
    pdf.set_text_color(30, 41, 59)
    pdf.multi_cell(180, 4.5, 
        "En aviation commerciale, aucun pilote ne prend les commandes d'un avion de ligne sans avoir "
        "passé des centaines d'heures dans un simulateur de vol réaliste. Le simulateur recrée les "
        "tempêtes, les pannes de réacteur, et les atterrissages d'urgence. Il n'a pas pour but de faire rêver, "
        "mais d'entraîner des réflexes de survie et d'éprouver les protocoles de sécurité.\n\n"
        "ShockDesk est exactement ce simulateur de vol pour le trader macro et le quant. Sur les marchés, "
        "les opinions sont gratuites, mais les erreurs coûtent cher. ShockDesk vous place aux commandes "
        "d'un book professionnel (actions, obligations, pétrole, or, devises, options) connecté aux données "
        "réelles de Yahoo Finance. Vous pouvez y tester vos scénarios de choc, mesurer vos grecques en temps "
        "réel et valider la solidité de votre gestion du risque sans risquer un seul centime.")
    
    pdf.ln(3)
    pdf.section_header("2. Les Quatre Piliers Fondamentaux de la Plateforme")
    
    # Grille 2x2 des piliers
    piliers = [
        ("Moteur Événementiel Blueshift", "Architecture standard de desk (initialize / handle_data) avec passage d'ordres réaliste, calcul de slippage et commissions."),
        ("Anticipation Point-in-Time", "Registre de prévisions inviolable (config/forecasts.json). Zéro fuite d'information du futur dans le passé."),
        ("Atelier d'Options & Grecques", "Pricing Black-Scholes européen, surface d'IV avec smile/skew, et simulateur de structures (strangle, butterfly, condor)."),
        ("Discipline & Boucle de Revue", "Scorecard honnête net du drift du benchmark, arrêt ex-ante des positions, et révision mensuelle sans réécriture.")
    ]
    
    y_box = pdf.get_y() + 1
    for i, (title, desc) in enumerate(piliers):
        col = i % 2
        row = i // 2
        bx = 15 + col * 92
        by = y_box + row * 27
        pdf.card_box(bx, by, 88, 24, bg_color=(248, 250, 252), border_color=(203, 213, 225))
        pdf.set_xy(bx + 3, by + 2)
        pdf.set_font(pdf.font_main, "B", 8.5)
        pdf.set_text_color(14, 116, 144) # Cyan 700
        pdf.cell(82, 4.5, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_xy(bx + 3, by + 7)
        pdf.set_font(pdf.font_main, "", 7.5)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(82, 3.8, desc)
    
    pdf.set_y(y_box + 58)
    pdf.section_header("3. Structure de ce Manuel d'Apprentissage")
    pdf.set_font(pdf.font_main, "", 8.5)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(180, 4.2,
        "• Page 2 : Les 12 mots clés indispensables expliqués simplement (vocabulaire quant & desk).\n"
        "• Page 3 : Votre premier backtest pas à pas (interface, configuration, exécution).\n"
        "• Page 4 : Lecture des résultats (cartes métriques, courbe d'équité, tableau d'attribution).\n"
        "• Page 5 : L'anticipation macro et le registre de prévisions (mécanique point-in-time).\n"
        "• Page 6 : L'exemple réel du choc pétrolier (Brent +18,5 % vs +5 %) et la révision de modèle.\n"
        "• Page 7 : L'atelier d'options & calculs détaillés des payoffs (strangle, butterfly, iron condor).\n"
        "• Page 8 : Les 3 portes d'entrée (URL, API, CLI) et la boucle mensuelle de revue.\n"
        "• Page 9 : Glossaire étendu & les 7 règles d'or de la gestion de risque ShockDesk.")

    # =========================================================================
    # PAGE 2 : LES 12 MOTS CLÉS EXPLIQUÉS EN LANGAGE SIMPLE
    # =========================================================================
    pdf.add_page()
    pdf.page_title("2", "LES 12 MOTS CLÉS DU TRADING QUANTITATIF", 
                   "Le lexique fondamental pour comprendre les métriques et piloter votre risque")

    mots = [
        ("1. Alpha (α)", "La surperformance pure générée par la stratégie au-delà des mouvements généraux du marché. Un alpha positif indique que vos choix apportent une vraie valeur ajoutée propre."),
        ("2. Beta (β)", "La sensibilité du portefeuille aux variations de son indice de référence (benchmark). Un beta de 1,20 signifie que si le marché monte de 1 %, votre book a tendance à monter de 1,20 %."),
        ("3. Ratio de Sharpe", "Le rendement excédentaire par unité de risque global (volatilité). Formule : (Rendement - Taux sans risque) / Volatilité. Au-dessus de 1,0 c'est bon ; au-dessus de 2,0 c'est remarquable."),
        ("4. Ratio de Sortino", "Variante du Sharpe qui ne pénalise que la volatilité baissière (les pertes). Il évite de pénaliser une stratégie qui enregistre de fortes hausses inattendues."),
        ("5. Max Drawdown", "La baisse maximale en pourcentage subie par le portefeuille entre son plus haut historique et son creux le plus bas. C'est l'indicateur clé de la souffrance financière et psychologique du trade."),
        ("6. Point-in-Time", "Principe absolu interdisant toute fuite d'information future (lookahead bias). À la date T, le code ne peut lire que les données et prévisions publiées strictement avant ou à T."),
        ("7. Volatilité Implicite (IV)", "L'estimation par le marché de l'agitation future du sous-jacent, déduite du cours des options via la formule de Black-Scholes. Plus l'IV est élevée, plus les options sont chères."),
        ("8. Prime (Premium)", "Le prix payé par l'acheteur d'une option au vendeur. Acheter une option crée un débit (coût) ; vendre une option génère un crédit (encaissement de prime)."),
        ("9. Strike (Prix d'exercice)", "Le cours prédéterminé auquel le détenteur de l'option a le droit d'acheter (Call) ou de vendre (Put) l'actif sous-jacent à l'échéance convenue."),
        ("10. Les Grecques (Greeks)", "Sensibilités de l'option : Delta (sensibilité au prix du sous-jacent), Gamma (accélération du Delta), Vega (impact d'une hausse d'IV), Theta (perte de valeur journalière due au temps)."),
        ("11. Drift & Benchmark", "Le drift est la dérive tendancielle naturelle du marché. Le benchmark est l'actif étalon (ex : S&P 500 ^GSPC). Toute performance doit être mesurée nette de l'effet de marée du benchmark."),
        ("12. Débit / Crédit / Carry", "Une structure à débit coûte de la prime à l'entrée (long gamma, risque limité). Une structure à crédit encaisse la prime à l'entrée (vendeur de temps/theta, gain plafonné, carry positif).")
    ]

    y_pos = 38
    for i, (mot, expl) in enumerate(mots):
        col = i % 2
        row = i // 2
        bx = 15 + col * 92
        by = y_pos + row * 38
        pdf.card_box(bx, by, 88, 35, bg_color=(255, 255, 255), border_color=(226, 232, 240))
        
        pdf.set_xy(bx + 3, by + 2)
        pdf.set_font(pdf.font_main, "B", 8.5)
        pdf.set_text_color(3, 105, 161) # Sky 700
        pdf.cell(82, 4.5, mot, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        pdf.set_xy(bx + 3, by + 7)
        pdf.set_font(pdf.font_main, "", 7.5)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(82, 3.8, expl)

    # =========================================================================
    # PAGE 3 : PREMIER BACKTEST PAS À PAS
    # =========================================================================
    pdf.add_page()
    pdf.page_title("3", "VOTRE PREMIER BACKTEST PAS À PAS",
                   "Guide pratique pour manipuler l'interface, configurer les paramètres et lancer une stratégie")

    pdf.section_header("1. Tour Guidé de l'Interface & du Bandeau Supérieur")
    pdf.set_font(pdf.font_main, "", 8.5)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(180, 4.2,
        "Lorsque vous arrivez sur https://shockdesk.onrender.com, vous découvrez une barre de contrôle "
        "supérieure qui pilote l'ensemble de la session. Chaque modification met à jour l'URL (forme Blueshift) :\n"
        "• Sélecteur de Stratégie : Charge le code Python correspondant dans l'éditeur.\n"
        "• Univers (Bundle) : global-macro (book multi-actifs), us-equities (actions + options), energy-shock...\n"
        "• Capital initial : Montant engagé (ex : 25 500 000 $ pour le book macro ou 100 000 $ en options).\n"
        "• Dates (Début / Fin) : Fenêtre temporelle d'analyse (ex : 2026-07-01 au 2026-08-28).\n"
        "• Badge Source de Données : Vert ('données réelles Yahoo Finance') ou Orange ('modèle factoriel synthétique').")

    pdf.ln(2)
    pdf.section_header("2. Anatomie d'un Script de Stratégie ShockDesk")
    
    code_text = (
        'def initialize(context):\n'
        '    # Définition des actifs et planification des exécutions\n'
        '    context.asset = symbol("BZ=F")\n'
        '    schedule_function(trade, date_rules.every_day())\n\n'
        'def trade(context, data):\n'
        '    # Lecture de la prévision active point-in-time (sans fuite)\n'
        '    f = get_forecast("BZ=F")\n'
        '    if f and f.sign > 0 and not context.portfolio.positions:\n'
        '        order_target_percent(context.asset, 0.30)   # 30 % d\'exposition brute\n'
        '        record(spot=data.current(context.asset, "close"), sign=f.sign)\n'
    )
    pdf.card_box(15, pdf.get_y(), 180, 40, bg_color=(241, 245, 249), border_color=(203, 213, 225))
    pdf.set_xy(18, pdf.get_y() + 2)
    pdf.set_font(pdf.font_mono, "", 7.5)
    pdf.set_text_color(15, 23, 42)
    for line in code_text.strip().split("\n"):
        pdf.cell(174, 4.2, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_y(pdf.get_y() + 4)
    pdf.section_header("3. Les 4 Étapes pour Exécuter Votre Premier Test")
    
    steps = [
        ("Étape 1 : Choisir la stratégie", "Dans le menu déroulant, sélectionnez 'shock-lab-oil.py' (le book publié de juillet 2026)."),
        ("Étape 2 : Paramétrer l'univers", "Sélectionnez l'univers 'global-macro', indiquez un capital de 25 500 000 $, dates du 2026-07-01 au 2026-08-28."),
        ("Étape 3 : Lancer le calcul", "Cliquez sur le bouton bleu 'Lancer le backtest' ou utilisez le raccourci clavier 'Ctrl + Entrée'."),
        ("Étape 4 : Analyser le résultat", "L'interface bascule automatiquement sur l'onglet Backtest avec les cartes de score et la courbe.")
    ]
    
    y_step = pdf.get_y() + 1
    for i, (stitle, sdesc) in enumerate(steps):
        pdf.card_box(15, y_step + i * 16, 180, 14, bg_color=(255, 255, 255), border_color=(226, 232, 240))
        pdf.set_xy(18, y_step + i * 16 + 2)
        pdf.set_font(pdf.font_main, "B", 8)
        pdf.set_text_color(14, 116, 144)
        pdf.cell(50, 4, stitle)
        pdf.set_font(pdf.font_main, "", 7.5)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(110, 4, sdesc, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # =========================================================================
    # PAGE 4 : LECTURE DES RÉSULTATS (CARTES, COURBE & ATTRIBUTION)
    # =========================================================================
    pdf.add_page()
    pdf.page_title("4", "COMMENT LIRE LES RÉSULTATS D'UN BACKTEST",
                   "Décrypter les métriques clés, interpréter la courbe d'équité et auditer l'attribution par ligne")

    pdf.section_header("1. Les Cartes Métriques Principales")
    
    cards = [
        ("P&L TOTAL & CAGR", "+385 544 $ (+1,51 %)", "Gain net en dollars et taux annualisé composé."),
        ("VOLATILITÉ & SHARPE", "Vol 2,19 % · Sharpe 2,26", "Rendement excédentaire par unité de risque."),
        ("MAX DRAWDOWN", "-0,04 %", "Perte maximale depuis le plus haut de la courbe."),
        ("SORTINO & CALMAR", "Sortino 168,1 · Calmar 235", "Résistance spécifique aux chocs baissiers."),
        ("WIN RATE & TRADES", "11,9 % · 21 transactions", "Fréquence des séances positives et volume d'ordres."),
        ("BENCHMARK (^GSPC)", "+2,51 % sur la fenêtre", "Performance de l'étalon de comparaison.")
    ]
    
    y_c = pdf.get_y() + 1
    for i, (title, val, desc) in enumerate(cards):
        col = i % 3
        row = i // 3
        bx = 15 + col * 61
        by = y_c + row * 22
        pdf.card_box(bx, by, 58, 20, bg_color=(248, 250, 252), border_color=(203, 213, 225))
        pdf.set_xy(bx + 2, by + 1.5)
        pdf.set_font(pdf.font_main, "B", 7)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(54, 3.5, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_xy(bx + 2, by + 5.5)
        pdf.set_font(pdf.font_main, "B", 8.5)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(54, 4.5, val, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_xy(bx + 2, by + 10.5)
        pdf.set_font(pdf.font_main, "", 6.5)
        pdf.set_text_color(71, 85, 105)
        pdf.multi_cell(54, 3, desc)

    pdf.set_y(y_c + 47)
    pdf.section_header("2. La Courbe d'Équité vs Benchmark et Zone de Drawdown")
    pdf.set_font(pdf.font_main, "", 8.5)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(180, 4.2,
        "Le graphique central trace l'évolution de la valeur liquidative du portefeuille (courbe bleue) comparée "
        "au S&P 500 (courbe grise). Deux leçons visuelles immédiates :\n"
        "• Profil de choc : La stratégie accélère violemment lors du choc pétrolier (semaine du 15 au 23 juillet) "
        "puis se stabilise après la prise de bénéfice au jour de pic.\n"
        "• Sous-graphique de Drawdown : En rouge sous la courbe, il montre les phases de creux. Un drawdown plat "
        "indique une excellente préservation du capital.")

    pdf.ln(2)
    pdf.section_header("3. Le Tableau d'Attribution du P&L : Qui a Payé, Qui a Coûté ?")
    
    attr_data = [
        ("BZ=F (Brent Crude Oil)", "+283 621 $", "+1,11 %", "La ligne porteuse du scénario haussier"),
        ("DBC (Matières premières)", "+61 026 $", "+0,24 %", "Contagion positive du complexe énergie"),
        ("^GSPC (S&P 500 - Short)", "+55 143 $", "+0,22 %", "Couverture macro : la baisse actions a payé"),
        ("TLT (Obligations US 20+)", "+27 364 $", "+0,11 %", "Refuge obligataire face aux tensions géopolitiques"),
        ("DX-Y.NYB (Dollar Index)", "+23 380 $", "+0,09 %", "Hausse du billet vert lors du choc"),
        ("HYG (High Yield Credit)", "+6 021 $", "+0,02 %", "Stabilité du crédit d'entreprises énergétiques"),
        ("GC=F (Or - Gold Futures)", "-71 012 $", "-0,28 %", "Le MISS de l'exercice : l'or a corrigé sous la hausse des taux réels")
    ]
    
    y_t = pdf.get_y() + 1
    pdf.set_fill_color(30, 41, 59)
    pdf.rect(15, y_t, 180, 6, style="F")
    pdf.set_font(pdf.font_main, "B", 7.5)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(18, y_t + 1)
    pdf.cell(75, 4, "SOUS-JACENT DU BOOK")
    pdf.cell(35, 4, "P&L RÉALISÉ ($)")
    pdf.cell(30, 4, "CONTRIBUTION")
    pdf.cell(40, 4, "RÔLE / DIAGNOSTIC", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    for idx, (sym, pnl, cont, role) in enumerate(attr_data):
        row_y = y_t + 6 + idx * 6.5
        bg = (248, 250, 252) if idx % 2 == 0 else (255, 255, 255)
        pdf.card_box(15, row_y, 180, 6.5, bg_color=bg, border_color=(241, 245, 249))
        pdf.set_xy(18, row_y + 1)
        pdf.set_font(pdf.font_main, "B" if idx == 0 or idx == 6 else "", 7.5)
        if "-" in pnl:
            pdf.set_text_color(220, 38, 38)
        elif "+" in pnl:
            pdf.set_text_color(16, 185, 129)
        else:
            pdf.set_text_color(15, 23, 42)
        pdf.cell(75, 4, sym)
        pdf.cell(35, 4, pnl)
        pdf.cell(30, 4, cont)
        pdf.set_font(pdf.font_main, "", 7)
        pdf.set_text_color(71, 85, 105)
        pdf.cell(40, 4, role, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # =========================================================================
    # PAGE 5 : L'ANTICIPATION & LE REGISTRE DE PRÉVISIONS
    # =========================================================================
    pdf.add_page()
    pdf.page_title("5", "L'ANTICIPATION & LE REGISTRE DE PRÉVISIONS",
                   "Comment formaliser des thèses macro ex-ante et auditer leur score sans tricher")

    pdf.section_header("1. Pourquoi Anticiper ? Sortir du Pur Data-Mining Rétroactif")
    pdf.set_font(pdf.font_main, "", 8.5)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(180, 4.2,
        "Le piège classique du backtesting quantitatif consiste à optimiser 50 paramètres sur le passé "
        "jusqu'à obtenir une courbe parfaite (overfitting). Dans ShockDesk, la démarche est inversée :\n"
        "• Vous formulez une thèse économique datée (un choc pétrolier, une baisse de taux, une hausse d'IV).\n"
        "• Cette thèse est consignée dans un registre persistant (config/forecasts.json) avec un numéro de révision.\n"
        "• Le moteur de backtest ne peut lire à la date du bar que la prévision en vigueur à cet instant précis.")

    pdf.ln(2)
    pdf.section_header("2. Anatomie d'une Entrée de Prévision (JSON)")
    
    json_text = (
        '{\n'
        '  "id": "shocklab-2026-07-oil",\n'
        '  "asset": "BZ=F", "benchmark": "^GSPC", "stop_date": "2026-08-05",\n'
        '  "revisions": [\n'
        '    {"rev": 1, "date": "2026-07-15", "sign": +1, "amplitude": 0.05,\n'
        '     "peak_day": 7, "reversion": -0.03, "iv_shift": 0.10, "confidence": 0.60,\n'
        '     "note": "v1 : Brent +5 % à J+7, puis retour à -3 % au stop calendar."}\n'
        '  ]\n'
        '}'
    )
    pdf.card_box(15, pdf.get_y(), 180, 42, bg_color=(241, 245, 249), border_color=(203, 213, 225))
    pdf.set_xy(18, pdf.get_y() + 2)
    pdf.set_font(pdf.font_mono, "", 7.5)
    pdf.set_text_color(15, 23, 42)
    for line in json_text.strip().split("\n"):
        pdf.cell(174, 4.2, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(pdf.get_y() + 4)
    pdf.section_header("3. Le Scorecard Honnête : Mesure Nette du Drift du Marché")
    pdf.set_font(pdf.font_main, "", 8.5)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(180, 4.2,
        "Le scorecard de l'onglet Anticipation compare la prévision publiée à la trajectoire réelle observée :\n"
        "1. Accord de signe net du drift (5/6 réussis) : Si le S&P 500 monte de 2 %, une action qui monte de 1 % "
        "a en réalité sous-performé. Le rendement est corrigé du beta * drift benchmark.\n"
        "2. Erreur de timing du pic (médiane 1,0 jour) : Mesure le décalage entre le jour prévu et le jour réel.\n"
        "3. Règle d'or de gouvernance : Seule la révision originale (rev 1) entre dans le score historique. "
        "Les révisions ultérieures permettent de piloter le futur mais n'embellissent jamais le passé.")

    # =========================================================================
    # PAGE 6 : L'EXEMPLE RÉEL DU CHOC PÉTROLIER & LA RÉVISION DE MODÈLE
    # =========================================================================
    pdf.add_page()
    pdf.page_title("6", "L'EXEMPLE RÉEL DU CHOC PÉTROLIER & RÉVISIONS",
                   "Étude du cas de juillet 2026 : Brent +18,5 % vs +5 % prévu, et le passage en grille d'amplitudes")

    pdf.section_header("1. La Chronologie Réelle : Prévision vs Marché")
    
    chrono = [
        ("15 Juillet 2026", "Publication", "Brent à 84,95 $. Modèle : hausse +5 %, pic attendu à J+7 (22 juillet), stop calendar au 05 août."),
        ("22 Juillet (J+7)", "Jour de Pic Modèle", "P&L du book au sommet (+178 k$). Le modèle indique la sortie optimale."),
        ("23 Juillet (J+8)", "Pic Réel Marché", "Brent culmine à +18,5 % (100,69 $). L'erreur de timing n'est que de 1 jour."),
        ("05 Août 2026", "Stop Calendar", "Reversion totale : Brent sous son niveau de départ (-6,5 %). P&L book figé à +99 k$.")
    ]
    
    y_ch = pdf.get_y() + 1
    for i, (date, badge, desc) in enumerate(chrono):
        by = y_ch + i * 16
        pdf.card_box(15, by, 180, 14, bg_color=(255, 255, 255), border_color=(226, 232, 240))
        pdf.set_xy(18, by + 2)
        pdf.set_font(pdf.font_main, "B", 8)
        pdf.set_text_color(3, 105, 161)
        pdf.cell(38, 4, date)
        pdf.set_font(pdf.font_main, "B", 7.5)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(42, 4, f"[{badge}]")
        pdf.set_font(pdf.font_main, "", 7.5)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(95, 4, desc, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(y_ch + 68)
    pdf.section_header("2. Les Deux Grandes Leçons de Desk")
    pdf.set_font(pdf.font_main, "", 8.5)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(180, 4.2,
        "• Leçon 1 : Le signal de timing a de la valeur, la vue directionnelle brute n'en a pas.\n"
        "  Sortir au jour de pic du modèle (J+7) figeait +178 k$ (+0,70 %). Attendre le stop calendar n'a "
        "  laissé que +99 k$ (+0,39 %). Le signal de timing a rapporté +79 k$ (31 points de base) à lui seul.\n"
        "• Leçon 2 : L'architecture multi-actifs protège contre l'erreur de prévision.\n"
        "  Au stop du 5 août, la ligne directionnelle Brent a fini en perte (-94 k$), mais le book global est "
        "  largement gagnant grâce à la position vendeuse sur le S&P 500 (+243 k$) et aux refuges.")

    pdf.ln(2)
    pdf.section_header("3. La Révision r2 : Passer d'un Chiffre Fixe à une Grille d'Amplitudes")
    pdf.set_font(pdf.font_main, "", 8.5)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(180, 4.2,
        "Face au constat d'une amplitude sous-estimée d'un facteur 3,7 (+18,5 % vs +5,0 %), la révision 2 "
        "introduit une grille : 'amplitude': [0.05, 0.10, 0.185] et 'peak_day': [7, 9].\n"
        "On ne cherche plus à deviner un niveau exact, mais on teste la résistance du book sur une fourchette "
        "de stress complète.")

    # =========================================================================
    # PAGE 7 : L'ATELIER D'OPTIONS & CALCULS DE PAYOFFS
    # =========================================================================
    pdf.add_page()
    pdf.page_title("7", "L'ATELIER D'OPTIONS & PAYOFFS CHIFFRÉS",
                   "Pricing Black-Scholes et calculs complets sur SPY (Spot = 642,00 $, Échéance 30 jours, r = 4,1 %)")

    strats = [
        ("Structure 1 : Long Strangle (Strikes 625 Put / 660 Call)",
         "Jambes : Achat Put 625 (4,80 $) + Achat Call 660 (5,88 $)\n"
         "Prime nette payée (Débit) : 10,69 $ • Perte maximale : 10,69 $\n"
         "Points morts (Breakevens) : 614,31 $ (-4,3 %) et 670,69 $ (+4,5 %)\n"
         "Payoff à l'échéance : Si SPY = 600 $ -> P&L = +14,31 $ | Si SPY = 640 $ -> P&L = -10,69 $ | Si SPY = 680 $ -> P&L = +9,31 $\n"
         "Usage : Achat de volatilité pure (long gamma) quand un choc violent est imminent."),
         
        ("Structure 2 : Call Butterfly (Strikes 620 / 640 / 660)",
         "Jambes : +1 Call 620 (27,69 $) / -2 Calls 640 (14,27 $) / +1 Call 660 (5,88 $)\n"
         "Prime nette payée (Débit) : 5,03 $ • Gain maximal : 14,97 $ (au corps à 640 $)\n"
         "Points morts : 625,03 $ et 654,97 $ • Perte maximale : 5,03 $ (au-delà des ailes)\n"
         "Payoff à l'échéance : Si SPY = 640 $ -> P&L = +14,97 $ (+297 % !) | Si SPY = 600 $ ou 680 $ -> P&L = -5,03 $\n"
         "Usage : Monétiser un timing exact sur un niveau cible avec risque strictement borné."),
         
        ("Structure 3 : Iron Condor (Strikes 620 / 630 / 650 / 660)",
         "Jambes : +1 Put 620 (3,61 $) / -1 Put 630 (6,27 $) / -1 Call 650 (9,45 $) / +1 Call 660 (5,88 $)\n"
         "Prime nette encaissée (Crédit) : 6,23 $ • Gain maximal : 6,23 $ (entre 630 $ et 650 $)\n"
         "Perte maximale : 3,77 $ (en dehors du range 620-660) • Points morts : 623,77 $ et 656,23 $\n"
         "Payoff à l'échéance : Si SPY reste à 642 $ -> P&L = +6,23 $ | Si SPY s'échappe à 600 $ -> P&L = -3,77 $\n"
         "Usage : Vente de prime (collecte de theta) en régime de range sans choc annoncé.")
    ]

    y_st = 36
    for i, (stitle, sbody) in enumerate(strats):
        by = y_st + i * 53
        pdf.card_box(15, by, 180, 50, bg_color=(248, 250, 252), border_color=(203, 213, 225))
        pdf.set_xy(18, by + 2.5)
        pdf.set_font(pdf.font_main, "B", 8.5)
        pdf.set_text_color(14, 116, 144)
        pdf.cell(174, 4.5, stitle, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        pdf.set_xy(18, by + 8)
        pdf.set_font(pdf.font_main, "", 7.5)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(174, 4.0, sbody)

    # =========================================================================
    # PAGE 8 : LES 3 PORTES D'ENTRÉE & LA BOUCLE MENSUELLE
    # =========================================================================
    pdf.add_page()
    pdf.page_title("8", "LES 3 PORTES D'ENTRÉE & REVUE MENSUELLE",
                   "Une grammaire unifiée : piloter la plateforme via URL, API REST ou Ligne de Commande")

    pdf.section_header("1. Les Trois Portes d'Entrée ShockDesk")
    
    portes = [
        ("1. URL Blueshift", "Partage instantané d'un backtest via lien direct :\n"
                             "/research/strategies/<id>/code?name=global-macro&startCapital=25500000&action=backtest"),
        ("2. API HTTP REST", "Exécution programmable en JSON :\n"
                             "curl -X POST localhost:8050/api/backtest -d '{\"strategy_id\":\"...\",\"name\":\"global-macro\"}'"),
        ("3. Ligne de Commande", "Automatisation et scripts cron :\n"
                                 "python -m shockdesk.cli backtest --strategy shock-lab-oil --name global-macro")
    ]
    
    y_p = pdf.get_y() + 1
    for i, (title, desc) in enumerate(portes):
        bx = 15
        by = y_p + i * 21
        pdf.card_box(bx, by, 180, 19, bg_color=(255, 255, 255), border_color=(226, 232, 240))
        pdf.set_xy(bx + 3, by + 2)
        pdf.set_font(pdf.font_main, "B", 8)
        pdf.set_text_color(3, 105, 161)
        pdf.cell(174, 4, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_xy(bx + 3, by + 6.5)
        pdf.set_font(pdf.font_mono, "", 7)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(174, 3.8, desc)

    pdf.set_y(y_p + 67)
    pdf.section_header("2. Le Rituel de la Boucle de Revue Mensuelle (CLI revue)")
    pdf.set_font(pdf.font_main, "", 8.5)
    pdf.set_text_color(51, 65, 85)
    pdf.multi_cell(180, 4.2,
        "La commande 'python -m shockdesk.cli revue --name global-macro' automatise le rituel de fin de mois en 4 étapes :\n"
        "1. Audit du Scorecard : Calcul des écarts de timing et de signe sur les prévisions échues.\n"
        "2. Proposition de Révisions : Génération automatique du JSON prêt à être validé et soumis en POST.\n"
        "3. Recalibration de Volatilité : Identification des sous-jacents dont la vol annuelle s'écarte de plus de 15 %.\n"
        "4. Tournoi des Stratégies : Comparaison des performances de chaque book face à la référence momentum.")

    pdf.ln(2)
    pdf.section_header("3. Commande de Recalibration Prête à l'Emploi")
    cmd_revue = "python -m shockdesk.cli revue --name global-macro --asof 2026-08-28 --window 45"
    pdf.card_box(15, pdf.get_y(), 180, 12, bg_color=(241, 245, 249), border_color=(203, 213, 225))
    pdf.set_xy(18, pdf.get_y() + 3.5)
    pdf.set_font(pdf.font_mono, "", 7.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(174, 5, cmd_revue, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # =========================================================================
    # PAGE 9 : GLOSSAIRE ÉTENDU & LES 7 RÈGLES D'OR DU TRADER
    # =========================================================================
    pdf.add_page()
    pdf.page_title("9", "GLOSSAIRE COMPLET & LES 7 RÈGLES D'OR",
                   "La charte de discipline indispensable pour opérer sur ShockDesk avec rigueur")

    pdf.section_header("1. Glossaire Complémentaire de Desk")
    
    glo_items = [
        ("MFE / MAE", "Maximum Favorable / Adverse Excursion. La plus grande hausse et la plus grande baisse latente vécues par le trade."),
        ("Smile & Skew", "La déformation de la surface de vol. Le skew reflète la prime accordée aux puts protecteurs face aux krachs."),
        ("Vega Crush", "L'effondrement brutal de la volatilité implicite immédiatement après la survenue d'un événement attendu (ex : pic du choc)."),
        ("Slippage", "L'écart d'exécution entre le prix théorique demandé et le prix réellement obtenu sur le marché lors d'un ordre au marché.")
    ]
    
    y_g = pdf.get_y() + 1
    for i, (gt, gd) in enumerate(glo_items):
        col = i % 2
        row = i // 2
        bx = 15 + col * 92
        by = y_g + row * 22
        pdf.card_box(bx, by, 88, 20, bg_color=(255, 255, 255), border_color=(226, 232, 240))
        pdf.set_xy(bx + 2, by + 1.5)
        pdf.set_font(pdf.font_main, "B", 7.5)
        pdf.set_text_color(3, 105, 161)
        pdf.cell(84, 3.5, gt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_xy(bx + 2, by + 5.5)
        pdf.set_font(pdf.font_main, "", 7)
        pdf.set_text_color(51, 65, 85)
        pdf.multi_cell(84, 3.2, gd)

    pdf.set_y(y_g + 48)
    pdf.section_header("2. Les Sept Règles d'Or du Trader ShockDesk")
    
    regles = [
        "1. Zéro fuite d'information : Une stratégie ne doit utiliser que des données point-in-time réelles.",
        "2. Nettoyer le drift de marché : Tout gain qui ne bat pas le benchmark passif n'est pas de l'alpha.",
        "3. Privilégier le timing à la prédiction de cours : Sortir au jour de pic protège l'essentiel du gain.",
        "4. Stresser sur une grille d'amplitudes : Ne pariez jamais sur un chiffre unique, testez une fourchette.",
        "5. Borner son risque avec des structures d'options : Préférez condors et butterflies aux ventes nues.",
        "6. Inviolabilité de l'historique : Corrigez vos prévisions via r2 sans jamais réécrire ou effacer r1.",
        "7. Recalibration systématique : Actualisez la matrice de volatilité à chaque revue mensuelle de desk."
    ]
    
    y_r = pdf.get_y() + 1
    for i, rtext in enumerate(regles):
        by = y_r + i * 8.5
        pdf.card_box(15, by, 180, 7.5, bg_color=(248, 250, 252), border_color=(203, 213, 225))
        pdf.set_xy(18, by + 1.5)
        pdf.set_font(pdf.font_main, "B", 7.5)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(174, 4.5, rtext, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Sauvegarde du fichier
    pdf.output(OUTPUT_PDF)
    print(f"PDF généré avec succès ({pdf.page_no()} pages) : {OUTPUT_PDF}")


if __name__ == "__main__":
    generate_pdf()
