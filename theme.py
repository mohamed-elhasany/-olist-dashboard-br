import streamlit as st

def inject():
    st.markdown(
        """
        <style>
        /* CSS VARIABLES FOR THEMES */
        :root {
            /* Dark Theme (Default) */
            --dark-bg: #1a1a1a;
            --dark-bg-gradient: linear-gradient(135deg, #1a1a1a 0%, #222222 100%);
            --dark-card: #242424;
            --dark-card-border: #3a3a3a;
            --dark-text-primary: #e8e6e3;
            --dark-text-secondary: #b0a9a2;
            --dark-text-warm: #d4b483;
            --dark-text-cool: #7fb4ca;
            --dark-accent: #2c8c6e;
            --dark-accent-hover: #23785d;
            --dark-sidebar: #1e1e1e;
            --dark-metric-bg: #242424;
            --dark-input-bg: #242424;
            --dark-slider-track: #3a3a3a;
            --dark-table-header: #2a2a2a;
            --dark-table-hover: #2f2f2f;
            --dark-scrollbar-track: #2a2a2a;
            --dark-scrollbar-thumb: #3a3a3a;
            --dark-tab-inactive: #2a2a2a;
            
            /* Light Theme */
            --light-bg: #f9f7f4;
            --light-bg-gradient: linear-gradient(135deg, #f9f7f4 0%, #f0ece6 100%);
            --light-card: #ffffff;
            --light-card-border: #e8e2d6;
            --light-text-primary: #2c2c2c;
            --light-text-secondary: #6b6b6b;
            --light-text-warm: #b8860b;
            --light-text-cool: #2e8b94;
            --light-accent: #2c8c6e;
            --light-accent-hover: #23785d;
            --light-sidebar: #ffffff;
            --light-metric-bg: #ffffff;
            --light-input-bg: #ffffff;
            --light-slider-track: #e8e2d6;
            --light-table-header: #f5f1ea;
            --light-table-hover: #f9f7f4;
            --light-scrollbar-track: #f0ece6;
            --light-scrollbar-thumb: #d4c4a9;
            --light-tab-inactive: #f5f1ea;
        }

        /* ROOT RESET */
        * { 
            border-radius: 0 !important;
        }
        /* Add transitions only to specific elements */
        .stButton > button,
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > div,
        .stCheckbox > label > div:first-child,
        .stRadio > label > div:first-child,
        .dataframe tr,
        .streamlit-expanderHeader,
        .stTabs [data-baseweb="tab"],
        ::-webkit-scrollbar-thumb,
        ::selection {
            transition: all 0.2s ease;
        }

        /* EXCLUDE plotly charts from transitions */
        .js-plotly-plot *,
        .plotly *,
        .stPlotlyChart *,
        [class*="plotly"] *,
        [class*="hover"] *,
        [class*="hoverlabel"] * {
            transition: none !important;
        }
        /* DEFAULT DARK THEME */
        .stApp { 
            background: var(--dark-bg-gradient);
        }

        /* TYPOGRAPHY */
        html, body, [class*="css"] { 
            font-family: 'Roboto', 'Segoe UI', system-ui, sans-serif;
            font-weight: 300;
        }

        /* TEXT COLORS - Dark Theme */
        .main-text { 
            color: var(--dark-text-primary);
            font-weight: 400;
        }
        
        .sub-text  { 
            color: var(--dark-text-secondary);
            font-weight: 300;
        }
        
        .warm-text {
            color: var(--dark-text-warm);
            font-weight: 400;
        }
        
        .cool-text {
            color: var(--dark-text-cool);
            font-weight: 400;
        }

        /* LIGHT THEME CLASS */
        .light-theme .stApp {
            background: var(--light-bg-gradient);
        }
        
        .light-theme .main-text { 
            color: var(--light-text-primary);
        }
        
        .light-theme .sub-text  { 
            color: var(--light-text-secondary);
        }
        
        .light-theme .warm-text {
            color: var(--light-text-warm);
        }
        
        .light-theme .cool-text {
            color: var(--light-text-cool);
        }

        /* HEADERS */
        h1 {
            color: var(--dark-text-primary);
            font-weight: 500;
            border-left: 4px solid var(--dark-text-warm);
            padding-left: 12px;
            margin-top: 1.5em;
            animation: fadeInDown 0.5s ease-out;
        }
        
        .light-theme h1 {
            color: var(--light-text-primary);
            border-left-color: var(--light-text-warm);
        }
        
        h2 {
            color: var(--dark-text-secondary);
            font-weight: 400;
            border-bottom: 1px solid var(--dark-card-border);
            padding-bottom: 8px;
            animation: fadeInLeft 0.5s ease-out 0.1s both;
        }
        
        .light-theme h2 {
            color: var(--light-text-secondary);
            border-bottom-color: var(--light-card-border);
        }
        
        h3 {
            color: var(--dark-text-secondary);
            font-weight: 400;
            animation: fadeInRight 0.5s ease-out 0.2s both;
        }
        
        .light-theme h3 {
            color: var(--light-text-secondary);
        }

        /* CARDS & CONTAINERS */
        .stCard {
            background-color: var(--dark-card);
            border: 1px solid var(--dark-card-border);
            padding: 20px;
            margin: 10px 0;
            animation: slideInUp 0.4s ease-out;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .light-theme .stCard {
            background-color: var(--light-card);
            border-color: var(--light-card-border);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        
        div[data-testid="stMetric"] {
            background-color: var(--dark-metric-bg);
            border: 1px solid var(--dark-card-border);
            padding: 15px;
            animation: pulseIn 0.6s ease-out;
        }
        
        .light-theme div[data-testid="stMetric"] {
            background-color: var(--light-metric-bg);
            border-color: var(--light-card-border);
        }
        
        div[data-testid="stMetric"] > div {
            color: var(--dark-text-primary) !important;
        }
        
        .light-theme div[data-testid="stMetric"] > div {
            color: var(--light-text-primary) !important;
        }
        
        div[data-testid="stMetricLabel"] {
            color: var(--dark-text-secondary) !important;
        }
        
        .light-theme div[data-testid="stMetricLabel"] {
            color: var(--light-text-secondary) !important;
        }
        
        div[data-testid="stMetricDelta"] svg {
            color: var(--dark-text-warm) !important;
        }
        
        .light-theme div[data-testid="stMetricDelta"] svg {
            color: var(--light-text-warm) !important;
        }

        /* ACCENT BUTTONS */
        .stButton > button {
            background-color: var(--dark-accent);
            color: #ffffff;
            border: none;
            border-radius: 2px;
            font-weight: 500;
            padding: 10px 24px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            font-size: 0.9em;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .stButton > button::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 5px;
            height: 5px;
            background: rgba(255, 255, 255, 0.5);
            opacity: 0;
            border-radius: 100%;
            transform: scale(1, 1) translate(-50%);
            transform-origin: 50% 50%;
        }
        
        .stButton > button:focus:not(:active)::after {
            animation: ripple 1s ease-out;
        }
        
        .stButton > button:hover {
            background-color: var(--dark-accent-hover);
            color: #ffffff;
            box-shadow: 0 8px 20px rgba(44, 140, 110, 0.3);
            transform: translateY(-2px);
        }
        
        .stButton > button:active {
            transform: translateY(0);
            box-shadow: 0 2px 10px rgba(44, 140, 110, 0.2);
            transition: all 0.1s ease;
        }

        /* INPUT WIDGETS */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > div {
            background-color: var(--dark-input-bg);
            color: var(--dark-text-primary);
            border: 1px solid var(--dark-card-border);
            transition: all 0.3s ease;
        }
        
        .light-theme .stTextInput > div > div > input,
        .light-theme .stNumberInput > div > div > input,
        .light-theme .stSelectbox > div > div > div {
            background-color: var(--light-input-bg);
            color: var(--light-text-primary);
            border-color: var(--light-card-border);
        }
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stSelectbox > div > div > div:focus {
            border-color: var(--dark-text-warm);
            box-shadow: 0 0 0 2px rgba(212, 180, 131, 0.2);
            transform: translateY(-1px);
        }
        
        .light-theme .stTextInput > div > div > input:focus,
        .light-theme .stNumberInput > div > div > input:focus,
        .light-theme .stSelectbox > div > div > div:focus {
            border-color: var(--light-text-warm);
            box-shadow: 0 0 0 2px rgba(184, 134, 11, 0.2);
        }

        /* SLIDERS */
        .stSlider > div > div > div {
            background-color: var(--dark-slider-track);
            transition: background-color 0.3s ease;
        }
        
        .light-theme .stSlider > div > div > div {
            background-color: var(--light-slider-track);
        }
        
        .stSlider > div > div > div > div {
            background-color: var(--dark-text-warm);
            transition: all 0.3s ease;
        }
        
        .light-theme .stSlider > div > div > div > div {
            background-color: var(--light-text-warm);
        }

        /* CHECKBOXES & RADIO */
        .stCheckbox > label,
        .stRadio > label {
            color: var(--dark-text-secondary);
            transition: color 0.3s ease;
        }
        
        .light-theme .stCheckbox > label,
        .light-theme .stRadio > label {
            color: var(--light-text-secondary);
        }
        
        .stCheckbox > label > div:first-child,
        .stRadio > label > div:first-child {
            background-color: var(--dark-input-bg);
            border-color: var(--dark-card-border);
            transition: all 0.3s ease;
        }
        
        .light-theme .stCheckbox > label > div:first-child,
        .light-theme .stRadio > label > div:first-child {
            background-color: var(--light-input-bg);
            border-color: var(--light-card-border);
        }
        
        .stCheckbox input:checked + div,
        .stRadio input:checked + div {
            background-color: var(--dark-text-warm) !important;
            border-color: var(--dark-text-warm) !important;
            animation: checkboxCheck 0.4s ease-out;
        }
        
        .light-theme .stCheckbox input:checked + div,
        .light-theme .stRadio input:checked + div {
            background-color: var(--light-text-warm) !important;
            border-color: var(--light-text-warm) !important;
        }

        /* DATA TABLES */
        .dataframe {
            background-color: var(--dark-card) !important;
            color: var(--dark-text-primary) !important;
            animation: fadeIn 0.6s ease-out;
        }
        
        .light-theme .dataframe {
            background-color: var(--light-card) !important;
            color: var(--light-text-primary) !important;
        }
        
        .dataframe th {
            background-color: var(--dark-table-header) !important;
            color: var(--dark-text-warm) !important;
            font-weight: 500;
            border-bottom: 2px solid var(--dark-card-border) !important;
            transition: all 0.3s ease;
        }
        
        .light-theme .dataframe th {
            background-color: var(--light-table-header) !important;
            color: var(--light-text-warm) !important;
            border-bottom-color: var(--light-card-border) !important;
        }
        
        .dataframe td {
            border-bottom: 1px solid var(--dark-card-border) !important;
            transition: background-color 0.2s ease;
        }
        
        .light-theme .dataframe td {
            border-bottom: 1px solid var(--light-card-border) !important;
        }
        
        .dataframe tr {
            transition: background-color 0.3s ease;
        }
        
        .dataframe tr:hover {
            background-color: var(--dark-table-hover) !important;
            transform: translateX(2px);
        }
        
        .light-theme .dataframe tr:hover {
            background-color: var(--light-table-hover) !important;
        }

        /* SIDEBAR */
        section[data-testid="stSidebar"] {
            background-color: var(--dark-sidebar);
            border-right: 1px solid var(--dark-card-border);
            animation: slideInLeft 0.4s ease-out;
        }
        
        .light-theme section[data-testid="stSidebar"] {
            background-color: var(--light-sidebar);
            border-right-color: var(--light-card-border);
        }
        
        section[data-testid="stSidebar"] .main-text {
            color: var(--dark-text-warm);
        }
        
        .light-theme section[data-testid="stSidebar"] .main-text {
            color: var(--light-text-warm);
        }
        
        /* SIDEBAR NAVIGATION */
        section[data-testid="stSidebar"] div[role="radiogroup"] label {
            color: var(--dark-text-secondary);
            padding: 12px 16px;
            margin: 4px 0;
            border-left: 3px solid transparent;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .light-theme section[data-testid="stSidebar"] div[role="radiogroup"] label {
            color: var(--light-text-secondary);
        }
        
        section[data-testid="stSidebar"] div[role="radiogroup"] label::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: var(--dark-text-warm);
            opacity: 0;
            transform: translateX(-100%);
            transition: all 0.3s ease;
            z-index: 0;
        }
        
        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background-color: var(--dark-table-header);
            border-left-color: var(--dark-text-warm);
            color: var(--dark-text-primary);
            padding-left: 20px;
        }
        
        .light-theme section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background-color: var(--light-table-header);
            border-left-color: var(--light-text-warm);
            color: var(--light-text-primary);
        }
        
        section[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] {
            background-color: transparent;
        }
        
        section[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"][aria-checked="true"] {
            background-color: var(--dark-table-header);
            border-left: 3px solid var(--dark-text-warm);
            color: var(--dark-text-primary);
            padding-left: 20px;
            animation: sidebarItemActive 0.4s ease-out;
        }
        

        .light-theme section[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"][aria-checked="true"] {
            background-color: var(--light-table-header);
            border-left-color: var(--light-text-warm);
            color: var(--light-text-primary);
        }

        /* EXPANDERS */
        .streamlit-expanderHeader {
            background-color: var(--dark-card);
            color: var(--dark-text-primary);
            border: 1px solid var(--dark-card-border);
            transition: all 0.3s ease;
        }
        
        .light-theme .streamlit-expanderHeader {
            background-color: var(--light-card);
            color: var(--light-text-primary);
            border-color: var(--light-card-border);
        }
        
        .streamlit-expanderHeader:hover {
            background-color: var(--dark-table-header);
            border-color: var(--dark-text-warm);
            transform: translateX(4px);
        }
        
        .light-theme .streamlit-expanderHeader:hover {
            background-color: var(--light-table-header);
            border-color: var(--light-text-warm);
        }

        /* TABS */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
            background-color: var(--dark-card);
            padding: 4px;
            animation: fadeIn 0.5s ease-out;
        }
        
        .light-theme .stTabs [data-baseweb="tab-list"] {
            background-color: var(--light-card);
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: var(--dark-tab-inactive);
            color: var(--dark-text-secondary);
            border-radius: 2px;
            padding: 10px 20px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .light-theme .stTabs [data-baseweb="tab"] {
            background-color: var(--light-tab-inactive);
            color: var(--light-text-secondary);
        }
        
        .stTabs [data-baseweb="tab"]::before {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 2px;
            background: var(--dark-text-warm);
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: var(--dark-text-warm) !important;
            color: var(--dark-bg) !important;
            font-weight: 500;
            transform: translateY(-1px);
        }
        
        .stTabs [aria-selected="true"]::before {
            transform: scaleX(1);
        }
        
        .light-theme .stTabs [aria-selected="true"] {
            background-color: var(--light-text-warm) !important;
            color: var(--light-bg) !important;
        }

        /* PROGRESS BARS */
        .stProgress > div > div > div {
            background-color: var(--dark-text-warm);
            animation: progressFill 2s ease-in-out infinite;
            background-image: linear-gradient(
                90deg,
                transparent,
                rgba(255, 255, 255, 0.3),
                transparent
            );
            background-size: 200% 100%;
        }
        
        .light-theme .stProgress > div > div > div {
            background-color: var(--light-text-warm);
        }

        /* SCROLLBARS */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
            transition: all 0.3s ease;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--dark-scrollbar-track);
        }
        
        .light-theme ::-webkit-scrollbar-track {
            background: var(--light-scrollbar-track);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--dark-scrollbar-thumb);
            transition: all 0.3s ease;
        }
        
        .light-theme ::-webkit-scrollbar-thumb {
            background: var(--light-scrollbar-thumb);
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--dark-text-warm);
            transform: scaleX(1.2);
        }
        
        .light-theme ::-webkit-scrollbar-thumb:hover {
            background: var(--light-text-warm);
        }

        /* SELECTION */
        ::selection {
            background-color: rgba(212, 180, 131, 0.3);
            color: var(--dark-text-primary);
            animation: selectionFlash 0.5s ease-out;
        }
        
        .light-theme ::selection {
            background-color: rgba(184, 134, 11, 0.2);
            color: var(--light-text-primary);
        }

        /* THEME SWITCHER STYLING */
        .theme-switch {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
        }
        
        .stButton > button {
            padding: 4px 12px !important;
            font-size: 0.85em !important;
        }
        
        .theme-switch button {
            background-color: var(--dark-card) !important;
            border: 1px solid var(--dark-card-border) !important;
            border-radius: 50% !important;
            width: 50px;
            height: 50px;
            padding: 0 !important;
            font-size: 1.5em !important;
            animation: themeSwitchFloat 3s ease-in-out infinite;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        
        .light-theme .theme-switch button {
            background-color: var(--light-card) !important;
            border-color: var(--light-card-border) !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        
        .theme-switch button:hover {
            transform: scale(1.1) rotate(180deg) !important;
            animation: none;
        }

        /* PLOT COMPATIBILITY - ENSURING PLOTS REMAIN UNCHANGED */
        .stPlotlyChart,
        .stPlotlyChart > div,
        .stPlotlyChart svg,
        .stPlotlyChart .js-plotly-plot,
        .stPlotlyChart .plot-container,
        .stPlotlyChart .main-svg,
        .stPlotlyChart .bg {
            background-color: transparent !important;
            background: transparent !important;
        }
        
        /* Ensure plot containers don't inherit dark backgrounds */
        div[data-testid="stPlotlyChart"],
        .stPlotlyChart {
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
        }
        
        /* Matplotlib/Plotly specific */
        .stPlotlyChart .modebar,
        .stPlotlyChart .modebar-container {
            background: transparent !important;
        }
        
        /* Chart containers */
        div[data-testid="element-container"] > div:has(.stPlotlyChart) {
            background: transparent !important;
        }
        
        /* ANIMATION KEYFRAMES */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeInLeft {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes fadeInRight {
            from {
                opacity: 0;
                transform: translateX(20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-100%);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes pulseIn {
            0% {
                opacity: 0;
                transform: scale(0.9);
            }
            70% {
                opacity: 1;
                transform: scale(1.05);
            }
            100% {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        @keyframes checkboxCheck {
            0% {
                transform: scale(0.8);
            }
            50% {
                transform: scale(1.1);
            }
            100% {
                transform: scale(1);
            }
        }
        
        @keyframes sidebarItemActive {
            0% {
                background-color: transparent;
            }
            100% {
                background-color: var(--dark-table-header);
            }
        }
        
        @keyframes progressFill {
            0% {
                background-position: -200% 0;
            }
            100% {
                background-position: 200% 0;
            }
        }
        
        @keyframes ripple {
            0% {
                transform: scale(0, 0);
                opacity: 0.5;
            }
            100% {
                transform: scale(20, 20);
                opacity: 0;
            }
        }
        
        @keyframes themeSwitchFloat {
            0%, 100% {
                transform: translateY(0);
            }
            50% {
                transform: translateY(-5px);
            }
        }
        
        @keyframes selectionFlash {
            0% {
                background-color: rgba(212, 180, 131, 0.1);
            }
            100% {
                background-color: rgba(212, 180, 131, 0.3);
            }
        }

        /* SMOOTH PAGE TRANSITIONS */
        .stApp {
            animation: pageLoad 0.5s ease-out;
        }
        
        @keyframes pageLoad {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }

        /* ENSURE NO INTERFERENCE WITH PLOTS */
        .js-plotly-plot .plotly,
        .js-plotly-plot .svg-container,
        .user-select-none,
        .plotly-graph-div {
            background: inherit !important;
            color-scheme: inherit !important;
        }
        
        /* Force plots to maintain their own styling */
        .stPlotlyChart *:not(.modebar):not(.modebar-container) {
            background: inherit !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

def theme_switcher():
    """Creates a theme toggle button"""
    # Initialize theme in session state
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'
    
    # Create HTML for theme switcher
    st.markdown(
        f"""
        <div class="theme-switch">
            <script>
            function toggleTheme() {{
                const body = document.body;
                const currentTheme = body.classList.contains('light-theme') ? 'light' : 'dark';
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                
                // Add transition class for smooth theme change
                body.classList.add('theme-transitioning');
                
                // Toggle theme class
                setTimeout(() => {{
                    body.classList.toggle('light-theme');
                    body.classList.remove('theme-transitioning');
                }}, 100);
                
                // Update Streamlit session state
                window.parent.postMessage({{
                    type: 'streamlit:setSessionState',
                    state: {{ theme: newTheme }}
                }}, '*');
                
                // Update button icon with animation
                const button = document.getElementById('theme-toggle-btn');
                button.style.transform = 'scale(0.8)';
                setTimeout(() => {{
                    button.innerHTML = newTheme === 'dark' ? '🌙' : '☀️';
                    button.style.transform = 'scale(1.1)';
                    setTimeout(() => {{
                        button.style.transform = 'scale(1)';
                    }}, 150);
                }}, 100);
            }}
            </script>
            <button id="theme-toggle-btn" onclick="toggleTheme()">
                {st.session_state.theme == 'dark' and '🌙' or '☀️'}
            </button>
        </div>
        """,
        unsafe_allow_html=True
    )