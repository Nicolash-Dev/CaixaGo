GLOBAL_STYLESHEET = '''
QWidget {
    background-color: #08111F;
    color: #F8FAFC;
    font-family: Arial;
    font-size: 14px;
}

#splashCard, #loginCard, #metricCard, #goCard, #timelineCard {
    background-color: #0E1A2B;
    border: 1px solid #1E3A5F;
    border-radius: 18px;
}

#sectionTitle {
    color: #F8FAFC;
    font-size: 18px;
    font-weight: 800;
}

#splashLogo, #brandMark {
    color: #2563EB;
    font-size: 48px;
    font-weight: 800;
}

#splashTitle, #headerBrand {
    color: #F8FAFC;
    font-size: 28px;
    font-weight: 800;
}

#splashSlogan, #splashStatus, #secondaryText {
    color: #94A3B8;
}

#pageTitle {
    color: #F8FAFC;
    font-size: 30px;
    font-weight: 800;
}

#cardTitle {
    color: #94A3B8;
    font-size: 14px; background-color: transparent;
    min-height: 18px;
}

#cardTitle, #secondaryText {
   color: #94A3B8;
    background-color: transparent;
    min-height: 18px;
}

#metricValue {
     color: #F8FAFC;
    font-size: 26px;
    font-weight: 800;
    background-color: transparent;
    min-height: 36px;
}

#metricCard {
    background-color: #0E1A2B;
    border: 1px solid #1E3A5F;
    border-radius: 22px;
}

#metricIconContainer {
    background-color: #0B1830;
    border: 1px solid #2563EB;
    border-radius: 36px;
}

#metricIcon {
    color: #60A5FA;
    background-color: transparent;
    font-size: 28px;
    font-weight: 800;
}

#cardTitle {
    color: #94A3B8;
    background-color: transparent;
    font-size: 16px;
    min-height: 22px;
}

#metricValue {
    color: #F8FAFC;
    background-color: transparent;
    font-size: 30px;
    font-weight: 800;
    min-height: 40px;
}

#secondaryText {
    color: #AFC1D9;
    background-color: transparent;
    font-size: 14px;
    min-height: 20px;
}

#goTitle {
    color: #60A5FA;
    font-size: 18px;
    font-weight: 800;
}

QLineEdit {
    background-color: #111C2D;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 14px;
    font-size: 20px;
    letter-spacing: 8px;
}

QLineEdit:focus {
    border: 1px solid #2563EB;
}

QPushButton {
    min-height: 52px;
    border-radius: 12px;
    padding: 0 22px;
    font-weight: 700;
}

#primaryButton {
    background-color: #2563EB;
    color: white;
    border: none;
}

#primaryButton:hover {
    background-color: #1D4ED8;
}

#primaryButton:pressed {
    background-color: #1E40AF;
}

#ghostButton {
    background-color: transparent;
    color: #94A3B8;
    border: 1px solid #334155;
}

#ghostButton:hover {
    color: #F8FAFC;
    border-color: #64748B;
}

#errorText {
    color: #F87171;
}

#successText {
    color: #4ADE80;
}

#warningBadge {
    color: #FBBF24;
    font-weight: 700;
}
#timelineRow {
    background-color: #111C2D;
    border: 1px solid #1E3A5F;
    border-radius: 10px;
}

#timelineDescription {
    color: #F8FAFC;
    background-color: transparent;
    font-weight: 700;
}

#timelinePositive {
    color: #4ADE80;
    background-color: transparent;
    font-weight: 800;
}

#timelineNegative {
    color: #F87171;
    background-color: transparent;
    font-weight: 800;
}
#timelineContent {
    background-color: transparent;
}

QScrollArea {
    background-color: transparent;
    border: none;
}

QScrollArea > QWidget > QWidget {
    background-color: transparent;
}

QScrollBar:vertical {
    background-color: #0E1A2B;
    width: 10px;
    margin: 0;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #334155;
    min-height: 30px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #475569;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background-color: transparent;
}

'''
