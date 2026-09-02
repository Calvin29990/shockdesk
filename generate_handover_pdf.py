import sys
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm

def build_pdf(filename="candidatures-reseau-fo/DOSSIER_DE_REPRISE_CHASSE_FO_CALVIN_MINANG.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    primary_color = colors.HexColor("#0f2b48")
    accent_color = colors.HexColor("#1b6ca8")
    dark_gray = colors.HexColor("#222222")
    light_bg = colors.HexColor("#f4f7f9")
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=accent_color,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=accent_color,
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=dark_gray,
        spaceAfter=4
    )

    bold_body_style = ParagraphStyle(
        'Bold_Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=dark_gray,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1a252f"),
        spaceAfter=3
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("🎯 DOSSIER DE REPRISE STRATÉGIQUE — CHASSE FRONT OFFICE", title_style))
    story.append(Paragraph("GUIDE MAÎTRE HANDOVER POUR PROCHAINE SESSION ARENA / AGENT IA", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=2, spaceAfter=10))

    # Profile Box
    profile_data = [
        [
            Paragraph("<b>Candidat :</b> Calvin Minang", body_style),
            Paragraph("<b>Formation :</b> SKEMA BS — M2 Finance de Marché (Bac+5)", body_style)
        ],
        [
            Paragraph("<b>Recherche :</b> Stage Fin d'Études FO (Janvier 2027, 6 mois)", body_style),
            Paragraph("<b>Contact :</b> +33 7 52 97 58 09 (WhatsApp/Tel)", body_style)
        ],
        [
            Paragraph("<b>Disponibilité :</b> Hors France jusqu'au 9 sept / À Paris dès le 10 sept 2026", body_style),
            Paragraph("<b>GitHub / Projets :</b> https://github.com/Calvin29990", body_style)
        ],
        [
            Paragraph("<b>Compétences Clés :</b> Bilingue FR/ES, Anglais pro, Python (Pricers Autocall/Monte-Carlo/Grecs temps réel, Terminal), VBA", body_style),
            Paragraph("<b>Cibles Prioritaires :</b> Structuration Dérivés, Trading/Market Making, Sales Cross-Asset, Quant", body_style)
        ]
    ]
    t_profile = Table(profile_data, colWidths=[8.5*cm, 8.5*cm])
    t_profile.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('BOX', (0,0), (-1,-1), 1, accent_color),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_profile)
    story.append(Spacer(1, 10))

    # SECTION 1
    story.append(Paragraph("1. DIRECTIVES IMPÉRATIVES POUR LE PROCHAIN AGENT IA", h1_style))
    story.append(Paragraph("Toute future IA reprenant ce projet DOIT respecter strictement les règles opérationnelles suivantes :", body_style))
    
    rules = [
        "<b>1. ZÉRO BANQUE FRANÇAISE CLASSIQUE :</b> Les banques françaises (BNP, SG, CACIB, Natixis) ont déjà été intensivement contactées lors des premières vagues. Ne plus les cibler SAUF en cas de post LinkedIn ultra-récent (< 24-48h).",
        "<b>2. PRIORITÉ ABSOLUE AUX BANQUES INTERNATIONALES TIER-1 (PARIS) :</b> Cibler exclusivement Goldman Sachs, Morgan Stanley, Bank of America, Barclays, Deutsche Bank, JPMorgan, Citi, UBS, Nomura à Paris.",
        "<b>3. INTERDICTION STRICTE DE KEPLER CHEUVREUX :</b> Retirer définitivement tout contact chez Kepler Cheuvreux (expérience décourageante signalée).",
        "<b>4. FOCUS FRANCE / PARIS :</b> Mettre en pause l'Espagne et la Suisse tant que la place de Paris n'a pas été saturée.",
        "<b>5. ENVOIS STRICTEMENT 1-À-1 :</b> Ne jamais regrouper plusieurs adresses dans un même mail (protection anti-spam bancaire). Format individuel systématique.",
        "<b>6. ACCROCHE LÉGITIME ET POLIE :</b> Mentionner la déduction de l'adresse professionnelle suite à leur rôle à la tête du desk, présenter directement le projet GitHub/Python et attacher le CV PDF."
    ]
    for r in rules:
        story.append(Paragraph(f"• {r}", body_style))
    story.append(Spacer(1, 8))

    # SECTION 2
    story.append(Paragraph("2. BILAN DES CONTACTS & HISTORIQUE DES ENVOIS EFFECTUÉS (SEPT 2026)", h1_style))
    story.append(Paragraph("Plus de 35 e-mails individuels ont été envoyés avec succès aujourd'hui. Ne JAMAIS re-contacter les personnes suivantes :", body_style))

    contacts_data = [
        ["Institution", "Décideurs & Desks Contactés (Délivrés avec succès)", "Statut"],
        ["Bank of America Paris", "Leonard Fienberg (MD Head Structuring), Amaury Gosselin (MD), Blaise Prévoteau (MD EGB Trading), Barbara Duval (Sales EQD)", "Envoyé"],
        ["Goldman Sachs Paris", "Guillaume Tropenat (ED Senior Sales Trader), Alberto Ricci (Global Markets)", "Envoyé"],
        ["Morgan Stanley Paris", "Antoine Varennes (ED Rates Sales), Megan Roland (ED Equity Sales Trader)", "Envoyé"],
        ["Deutsche Bank Paris", "Jean-Benoît Bouges (MD DCM), Fabrice Haffner (Director Fixed Income Sales)", "Envoyé"],
        ["Barclays Paris", "Guillaume Chouabi (Sales Structurés), Audrey Berthe (Sales FX & Rates)", "Envoyé"],
        ["UBS Paris", "Jérémy Bracci (Director Structured Products Solutions)", "Envoyé"],
        ["Citi Paris", "Matthieu Boistard (Global Markets Front Office)", "Envoyé"],
        ["HSBC Paris", "Jérôme Lemue (Head of Corporate Equity Derivatives)", "Envoyé"],
        ["Amundi Paris", "Paul Guiraud (Derivatives Pricing), Maamoun Mekki (Quant), PENG Yao (Structuration)", "Envoyé"],
        ["BRED Salle Marchés", "Benjamin Dussault (Senior Structurer EQD), Joël Pacevicius (Trader EQD), Desk FO", "Envoyé"],
        ["SGCIB / Natixis / CACIB", "David Attar (ETF Trading), Quentin Sattler (Risk Vol), Anastasia Ifergan (Convertibles), etc.", "Envoyé"]
    ]
    t_contacts = Table(contacts_data, colWidths=[4*cm, 11*cm, 2*cm])
    t_contacts.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('LEADING', (0,0), (-1,-1), 9.5),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#dcdcdc")),
        ('PADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_contacts)
    story.append(Spacer(1, 8))

    # SECTION 3 : Bounces
    story.append(Paragraph("3. LISTE NOIRE DES ADRESSES AYANT REJETÉ LES MAILS (BOUNCES)", h1_style))
    story.append(Paragraph("Les adresses suivantes sont rejetées par les serveurs bancaires (alias masqués ou blocage externe) — <b>NE PLUS UTILISER</b> :", body_style))
    story.append(Paragraph("<code>jean-loic.beibro@socgen.com</code>, <code>mathis.postec@ca-cib.com</code>, <code>arsene.delpierre@ca-cib.com</code>, <code>theodore.rousseau@ca-cib.com</code>, <code>luca.ciampi-ruiz@gs.com</code>, <code>mikael.aboucaya@cic.fr</code>, <code>hamza.belkouch@sgcib.com</code>, <code>matthieu.boisot@jpmorgan.com</code>, <code>sophie.farivarz@jpmorgan.com</code>, <code>anne-helene.illich@gs.com</code>.", code_style))
    story.append(Spacer(1, 8))

    # SECTION 4 : Master Snipping Template
    story.append(Paragraph("4. FORMAT DU PROMPT DE SORTIE ATTENDU DE L'IA (EXEMPLE TYPE)", h1_style))
    story.append(Paragraph("Lorsque l'utilisateur demande de nouvelles cibles, la future IA doit fournir directement le bloc prêt au copier-coller avec l'e-mail, l'objet et le corps personnalisé valorisant Python/GitHub et la logistique du candidat :", body_style))

    sample_box = [
        [Paragraph("<b>🔹 Destinataire :</b> <code>prenom.nom@domaine.com</code><br/>"
                   "<b>🔹 Objet :</b> <code>Candidature Stage Front Office / [Nom du Desk] — Calvin Minang (Janvier 2027)</code><br/>"
                   "<b>🔹 Corps :</b><br/>"
                   "<i>Bonjour [Prénom],<br/>"
                   "Je me permets de vous contacter directement ayant déduit votre adresse suite à la découverte de vos responsabilités à la tête de [Nom du Desk] chez [Banque] à Paris.<br/>"
                   "En dernière année de Bac+5 en finance de marché à SKEMA Business School, je développe en Python mes propres outils quantitatifs de desk : simulateur de valorisation d'options et structures à barrières (Autocalls Athena/Phoenix, Monte-Carlo, grecs en temps réel) et terminal de marché (https://github.com/Calvin29990).<br/>"
                   "Je maîtrise Python et Excel/VBA, et je suis bilingue français / espagnol. Je serais honoré d'apporter ma rigueur et ma réactivité au service de votre desk.<br/>"
                   "Précision logistique : je suis joignable au +33 7 52 97 58 09 jusqu'au 9 septembre et disponible en présentiel à Paris dès le 10 septembre.<br/>"
                   "Mon CV est joint à ce mail. Merci pour votre temps et excellente journée.<br/>"
                   "Bien cordialement, Calvin Minang</i>", body_style)]
    ]
    t_sample = Table(sample_box, colWidths=[17*cm])
    t_sample.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('BOX', (0,0), (-1,-1), 1, accent_color),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_sample)
    story.append(Spacer(1, 8))

    # SECTION 5 : Next Steps
    story.append(Paragraph("5. CALENDRIER D'ACTION & ÉVÉNEMENTS CLÉS (SEPTEMBRE 2026)", h1_style))
    story.append(Paragraph("• <b>Jeudi 3 - Vendredi 4 Septembre :</b> Surveillance des retours d'e-mails (créneaux 7h30-8h30 et 18h30-20h00).<br/>"
                           "• <b>Mardi 8 - Mercredi 9 Septembre :</b> Lancement des relances douces à J+6 / J+7 pour les décideurs n'ayant pas encore répondu.<br/>"
                           "• <b>Mardi 15 Septembre 2026 :</b> <b>SKEMA Finance Day 2026</b> en présentiel au Campus Grand Paris (5 quai Marcel Dassault, Suresnes) — Job-dating avec 30+ institutions, sessions de recrutement direct et Golden Tickets.", body_style))

    doc.build(story)
    print("PDF generated successfully:", filename)

if __name__ == "__main__":
    build_pdf()
