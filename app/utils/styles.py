GLOBAL_STYLESHEET = '''
QWidget {
    background-color: #08111F;
    color: #F8FAFC;
    font-family: Arial;
    font-size: 14px;
}

#splashCard, #loginCard, #metricCard, #goCard {
    background-color: #0E1A2B;
    border: 1px solid #1E3A5F;
    border-radius: 18px;
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
    font-size: 14px;
}

#metricValue {
    color: #F8FAFC;
    font-size: 28px;
    font-weight: 800;
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
    min-height: 44px;
    border-radius: 12px;
    padding: 0 20px;
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
'''
