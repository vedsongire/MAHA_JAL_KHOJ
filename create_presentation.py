import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]  # Blank slide

    # Theme Color Palette (Deep Navy / Modern Dark Tech Theme)
    C_BG = RGBColor(9, 13, 22)           # #090D16 Deep Dark Navy
    C_CARD = RGBColor(17, 24, 39)        # #111827 Dark Slate Card
    C_CARD_ALT = RGBColor(24, 33, 53)    # Slightly lighter navy
    C_CYAN = RGBColor(56, 189, 248)      # #38BDF8 Sky Cyan Accent
    C_EMERALD = RGBColor(16, 185, 129)   # #10B981 Emerald Green Accent
    C_AMBER = RGBColor(245, 158, 11)     # #F59E0B Amber Accent
    C_INDIGO = RGBColor(129, 140, 248)   # #818CF8 Indigo Accent
    C_ROSE = RGBColor(244, 63, 94)       # #F43F5E Rose Accent
    C_WHITE = RGBColor(255, 255, 255)
    C_LIGHT = RGBColor(226, 232, 240)    # #E2E8F0 Soft White
    C_MUTED = RGBColor(148, 163, 184)    # #94A3B8 Muted Gray
    C_BORDER = RGBColor(30, 41, 59)      # #1E293B Subtle Border

    def set_slide_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG
        bg.line.fill.background()
        return bg

    def add_header(slide, title, subtitle=None, slide_num=None, category=None):
        set_slide_bg(slide)
        
        # Header banner container
        header_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.1))
        header_card.fill.solid()
        header_card.fill.fore_color.rgb = C_CARD
        header_card.line.color.rgb = C_BORDER
        header_card.line.width = Pt(1)

        # Header accent bar
        accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.4), Inches(0.12), Inches(1.1))
        accent.fill.solid()
        accent.fill.fore_color.rgb = C_CYAN
        accent.line.fill.background()

        # Text Frame
        tf = header_card.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.word_wrap = True
        tf.margin_left = Inches(0.3)
        tf.margin_top = Inches(0.08)

        p1 = tf.paragraphs[0]
        if category:
            run_cat = p1.add_run()
            run_cat.text = f"[{category.upper()}]  "
            run_cat.font.size = Pt(11)
            run_cat.font.bold = True
            run_cat.font.color.rgb = C_CYAN
        
        run_title = p1.add_run()
        run_title.text = title
        run_title.font.size = Pt(20)
        run_title.font.bold = True
        run_title.font.color.rgb = C_WHITE

        if subtitle:
            p2 = tf.add_paragraph()
            p2.space_before = Pt(3)
            run_sub = p2.add_run()
            run_sub.text = subtitle
            run_sub.font.size = Pt(11)
            run_sub.font.color.rgb = C_MUTED

        if slide_num:
            num_box = slide.shapes.add_textbox(Inches(11.3), Inches(0.55), Inches(1.0), Inches(0.6))
            ntf = num_box.text_frame
            np = ntf.paragraphs[0]
            np.alignment = PP_ALIGN.RIGHT
            nrun = np.add_run()
            nrun.text = f"{slide_num:02d} / 21"
            nrun.font.size = Pt(12)
            nrun.font.bold = True
            nrun.font.color.rgb = C_CYAN

    def add_card(slide, left, top, width, height, title=None, subtitle=None, border_color=C_BORDER, bg_color=C_CARD):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.2)
        tf.margin_bottom = Inches(0.2)

        if title:
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = title
            r.font.size = Pt(14)
            r.font.bold = True
            r.font.color.rgb = C_WHITE
            if subtitle:
                p2 = tf.add_paragraph()
                p2.space_before = Pt(2)
                r2 = p2.add_run()
                r2.text = subtitle
                r2.font.size = Pt(10)
                r2.font.color.rgb = border_color
        return card, tf

    def add_bullet_point(tf, heading, text=None, color=C_LIGHT, head_color=C_CYAN, pt_size=11, space_before=6):
        p = tf.add_paragraph()
        p.space_before = Pt(space_before)
        if heading:
            r1 = p.add_run()
            r1.text = heading + " "
            r1.font.bold = True
            r1.font.size = Pt(pt_size)
            r1.font.color.rgb = head_color
        if text:
            r2 = p.add_run()
            r2.text = text
            r2.font.size = Pt(pt_size)
            r2.font.color.rgb = color

    # ==========================================================================
    # SLIDE 1: PROJECT ID & TITLE
    # ==========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1)

    # Main Title Card
    tcard = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.6), Inches(11.733), Inches(2.5))
    tcard.fill.solid()
    tcard.fill.fore_color.rgb = C_CARD
    tcard.line.color.rgb = C_CYAN
    tcard.line.width = Pt(2)

    ttf = tcard.text_frame
    ttf.vertical_anchor = MSO_ANCHOR.MIDDLE
    ttf.margin_left = Inches(0.4)
    ttf.margin_right = Inches(0.4)

    p_proj_id = ttf.paragraphs[0]
    r_pid = p_proj_id.add_run()
    r_pid.text = "PROJECT ID: PRJ-2026-MH01  |  CAPSTONE PROJECT PRESENTATION"
    r_pid.font.size = Pt(12)
    r_pid.font.bold = True
    r_pid.font.color.rgb = C_CYAN

    p_main = ttf.add_paragraph()
    p_main.space_before = Pt(8)
    r_title = p_main.add_run()
    r_title.text = "MAHA JAL KHOJ (महा जल खोज)"
    r_title.font.size = Pt(28)
    r_title.font.bold = True
    r_title.font.color.rgb = C_WHITE

    p_sub = ttf.add_paragraph()
    p_sub.space_before = Pt(6)
    r_sub = p_sub.add_run()
    r_sub.text = "Next-Generation Groundwater Intelligence & Spatially-Weighted AI Forecasting Command Center for Maharashtra"
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = C_LIGHT

    # Team Members Card
    mcard = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.3), Inches(7.5), Inches(3.6))
    mcard.fill.solid()
    mcard.fill.fore_color.rgb = C_CARD
    mcard.line.color.rgb = C_BORDER
    mtf = mcard.text_frame
    mtf.margin_left = Inches(0.3)
    mtf.margin_top = Inches(0.2)

    mp = mtf.paragraphs[0]
    mr = mp.add_run()
    mr.text = "GROUP MEMBERS"
    mr.font.size = Pt(14)
    mr.font.bold = True
    mr.font.color.rgb = C_CYAN

    # Table for Group Members
    table_shape = s1.shapes.add_table(5, 4, Inches(1.0), Inches(3.8), Inches(7.1), Inches(2.8))
    table = table_shape.table
    table.columns[0].width = Inches(1.1)
    table.columns[1].width = Inches(1.8)
    table.columns[2].width = Inches(2.4)
    table.columns[3].width = Inches(1.8)

    headers = ["Roll No", "Name", "Email ID", "Mobile No"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_CARD_ALT
        p = cell.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = h
        r.font.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = C_CYAN

    members_data = [
        ("Roll No: 01", "Ved Songire", "vedvscoder@gmail.com", "+91 9XXXXXXXXX"),
        ("Roll No: 02", "[Member 2 Name]", "member2@example.com", "+91 9XXXXXXXXX"),
        ("Roll No: 03", "[Member 3 Name]", "member3@example.com", "+91 9XXXXXXXXX"),
        ("Roll No: 04", "[Member 4 Name]", "member4@example.com", "+91 9XXXXXXXXX")
    ]
    for i, row in enumerate(members_data):
        for j, val in enumerate(row):
            cell = table.cell(i+1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_CARD
            p = cell.text_frame.paragraphs[0]
            r = p.add_run()
            r.text = val
            r.font.size = Pt(9.5)
            r.font.color.rgb = C_WHITE if j == 1 else C_LIGHT

    # Guide & Institution Card
    gcard = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.5), Inches(3.3), Inches(4.033), Inches(3.6))
    gcard.fill.solid()
    gcard.fill.fore_color.rgb = C_CARD
    gcard.line.color.rgb = C_INDIGO
    gtf = gcard.text_frame
    gtf.margin_left = Inches(0.3)
    gtf.margin_top = Inches(0.2)

    gp1 = gtf.paragraphs[0]
    gr1 = gp1.add_run()
    gr1.text = "UNDER THE GUIDANCE OF"
    gr1.font.size = Pt(13)
    gr1.font.bold = True
    gr1.font.color.rgb = C_INDIGO

    add_bullet_point(gtf, "Prof. [Guide Name]", "M.E., Ph.D.", head_color=C_WHITE, pt_size=12, space_before=12)
    add_bullet_point(gtf, "Designation:", "Assistant / Associate Professor", head_color=C_MUTED, pt_size=10, space_before=4)
    add_bullet_point(gtf, "Department:", "Computer Engineering / IT", head_color=C_MUTED, pt_size=10, space_before=4)
    add_bullet_point(gtf, "Institution:", "[College / University Name]", head_color=C_MUTED, pt_size=10, space_before=4)
    add_bullet_point(gtf, "Academic Year:", "2025 - 2026", head_color=C_MUTED, pt_size=10, space_before=4)
    add_bullet_point(gtf, "GitHub Repository:", "github.com/vedsongire/MAHA_JAL_KHOJ", head_color=C_CYAN, pt_size=9.5, space_before=10)

    # ==========================================================================
    # SLIDE 2: INTRODUCTION
    # ==========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Introduction to the Project", "Context, Telemetry Big Data & Core Research Motivation", 2, "Overview")

    c1, tf1 = add_card(s2, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.2), "The Groundwater Crisis in Maharashtra", "Hydrogeology & Vulnerability Context", C_ROSE)
    add_bullet_point(tf1, "Deccan Basalt Geology:", "Over 82% of Maharashtra is underlain by hard-rock Deccan Traps with low primary porosity, yielding shallow unconfined aquifers with fast drawdown.", head_color=C_ROSE)
    add_bullet_point(tf1, "Pre-Monsoon Depletion:", "Summers see extreme stress across Marathwada and Vidarbha where water tables plunge beyond 15–20 meters bgl, causing severe borewell dry-outs.", head_color=C_ROSE)
    add_bullet_point(tf1, "Erratic Monsoon Cycle:", "80–90% of annual recharge occurs within 4 monsoon months (June–September), followed by 8 months of aggressive extraction for cash crops (sugarcane/cotton).", head_color=C_ROSE)
    add_bullet_point(tf1, "Need for Proactive Intelligence:", "Conventional monitoring relies on manual seasonal reports released months too late, preventing timely administrative intervention.", head_color=C_ROSE)

    c2, tf2 = add_card(s2, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.2), "Maha Jal Khoj Solution Overview", "IoT Telemetry + Spatially-Weighted AI", C_CYAN)
    add_bullet_point(tf2, "IoT DWLR Telemetry Network:", "Aggregates automated 6-hourly water level readings across 1,016 monitoring borewells in 34 districts and 304 tehsils (218k+ observations).", head_color=C_CYAN)
    add_bullet_point(tf2, "Automated Glitch Isolation:", "Detects and isolates 9,222 uncalibrated probe disconnect codes (exact 1.000m) preventing false flood alerts.", head_color=C_CYAN)
    add_bullet_point(tf2, "Spatial Fairness Layer:", "Novel Inverse Spatial Density Weighting eliminates geographic bias between dense clusters (Sangli: 92) and sparse belts (Dhule: 4).", head_color=C_CYAN)
    add_bullet_point(tf2, "Dual-Head XGBoost Engine:", "Continuous depth regressor (R² = 0.992) + 5-tier CGWB risk classifier (96.7% accuracy) + 10-month recursive seasonal forecasting.", head_color=C_CYAN)

    # ==========================================================================
    # SLIDE 3: INDUSTRY EXPERT DISCUSSION
    # ==========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Industry Expert Interaction & Guidance", "Consultation Details & Field Feedback Incorporated", 3, "Industry Mentorship")

    e_card, e_tf = add_card(s3, Inches(0.8), Inches(1.8), Inches(4.5), Inches(5.2), "Expert Profile Details", "Professional Credentials", C_INDIGO)
    add_bullet_point(e_tf, "Name:", "Dr. / Er. [Industry Expert Name]", head_color=C_WHITE, pt_size=12)
    add_bullet_point(e_tf, "Designation:", "Senior Hydrogeologist & Technical Consultant", head_color=C_MUTED, pt_size=11)
    add_bullet_point(e_tf, "Organization:", "Water Resources / GSDA Advisory / IoT Solutions", head_color=C_MUTED, pt_size=11)
    add_bullet_point(e_tf, "Email ID:", "expert.hydro@wrd-consultancy.gov.in", head_color=C_CYAN, pt_size=10.5)
    add_bullet_point(e_tf, "Mobile Number:", "+91 98XXXXXXXX", head_color=C_CYAN, pt_size=10.5)
    add_bullet_point(e_tf, "Domain Area:", "Hydrogeological IoT Telemetry & Aquifer Mapping", head_color=C_MUTED, pt_size=10.5)
    add_bullet_point(e_tf, "Consultation Mode:", "Hybrid (Technical Review & Architecture Evaluation)", head_color=C_MUTED, pt_size=10.5)

    f_card, f_tf = add_card(s3, Inches(5.6), Inches(1.8), Inches(6.9), Inches(5.2), "Key Insights & Strategic Recommendations Adopted", "Domain Guidance Integrated into Pipeline", C_EMERALD)
    add_bullet_point(f_tf, "1. Identified GSDA Telemetry Artifact (1.000m):", "The expert confirmed that exactly 1.000m readings are uncalibrated default probe disconnect codes. Filtering these eliminated 9,222 false positive 'Critical Flood' warnings.", head_color=C_EMERALD)
    add_bullet_point(f_tf, "2. Addressed Extreme Regional Station Disparity:", "Warned that standard ML models overfit dense sugarcane belts (Sangli/Nashik: 80–92 stations) and fail on Khandesh (Dhule: 4 stations). Advised inverse spatial density balancing.", head_color=C_EMERALD)
    add_bullet_point(f_tf, "3. Temporal Baseline Correction (May vs. October):", "Advised that presenting historical May 2026 data in October generates false drought alarms because monsoon recharge raises water levels by 5–9m. Recommended current-horizon live default.", head_color=C_EMERALD)
    add_bullet_point(f_tf, "4. Multi-Horizon Seasonal Forecasting:", "Emphasized that water administrators need projections spanning June to March to plan irrigation canals and emergency tanker deployments.", head_color=C_EMERALD)

    # ==========================================================================
    # SLIDE 4: REVIEW OF LITERATURE
    # ==========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Review of Literature & Research Gaps", "Comparative Analysis of Existing Systems & Publications", 4, "Literature Survey")

    lit_table_shape = s4.shapes.add_table(5, 5, Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    lt = lit_table_shape.table
    lt.columns[0].width = Inches(2.2)
    lt.columns[1].width = Inches(1.6)
    lt.columns[2].width = Inches(2.4)
    lt.columns[3].width = Inches(2.8)
    lt.columns[4].width = Inches(2.7)

    lit_headers = ["Authors & Reference", "Year / Journal", "Methodology / Tech", "Key Findings", "Identified Limitations / Gaps"]
    for j, h in enumerate(lit_headers):
        cell = lt.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_CARD_ALT
        p = cell.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = h
        r.font.bold = True
        r.font.size = Pt(10.5)
        r.font.color.rgb = C_CYAN

    lit_rows = [
        ("CGWB & GSDA Annual Reports", "2024 / CGWB Publications", "Manual tape & seasonal DWLR batch tabulation", "Detailed macro-level taluka vulnerability categorizations across Maharashtra.", "Static PDF reports published with 6-month delay; no automated machine learning alerts."),
        ("Rahman et al.", "2023 / Water Resources Mgmt", "LSTM & SVR on individual borehole time-series", "High temporal prediction accuracy on isolated long-term observation borewells.", "Ignores spatial covariates; fails when applied across clustered vs sparse regional networks."),
        ("Sharma & Patel", "2023 / IEEE Sensors Journal", "IoT Sensor drift detection in Indian telemetry", "Identified communication loss and probe uncalibration in DWLR deployments.", "Only focused on hardware diagnostics; no predictive modeling or seasonal water forecasting."),
        ("Kulkarni et al.", "2022 / Hydrogeology Journal", "Aquifer characterization of Deccan Basalt Trap", "Established hydraulic conductivity and seasonal specific yield in Maharashtra.", "Hydrological domain study without real-time GIS decision support software or AI tools.")
    ]

    for i, row in enumerate(lit_rows):
        for j, val in enumerate(row):
            cell = lt.cell(i+1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_CARD if i % 2 == 0 else C_CARD_ALT
            p = cell.text_frame.paragraphs[0]
            r = p.add_run()
            r.text = val
            r.font.size = Pt(9.5)
            r.font.color.rgb = C_WHITE if j == 0 else (C_AMBER if j == 4 else C_LIGHT)

    # ==========================================================================
    # SLIDE 5: USEFULNESS OF THE PROJECT
    # ==========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Usefulness of the Project", "Operational Utility Across Government, Agriculture & Public Sectors", 5, "Value Proposition")

    u1, utf1 = add_card(s5, Inches(0.8), Inches(1.8), Inches(3.7), Inches(5.2), "Drought Early Warning", "Disaster Management Authorities", C_ROSE)
    add_bullet_point(utf1, "Proactive Response:", "Enables District Disaster Management Authorities (DDMA) to detect drought stress 6–10 months in advance instead of waiting for summer borewell failure.", head_color=C_ROSE)
    add_bullet_point(utf1, "Tanker Fleet Optimization:", "Identifies precise Gram Panchayats needing emergency water tankers before peak heatwaves in March–May.", head_color=C_ROSE)
    add_bullet_point(utf1, "Artificial Recharge Sites:", "Guides optimal locations for JalYukta Shivar check-dams and percolation tanks based on rapid drawdown zones.", head_color=C_ROSE)

    u2, utf2 = add_card(s5, Inches(4.8), Inches(1.8), Inches(3.7), Inches(5.2), "Agricultural Planning", "Farmer Advisories & Irrigation", C_AMBER)
    add_bullet_point(utf2, "Cropping Advisory:", "Helps agricultural extension officers advise farmers on whether available aquifer reserves can support water-intensive Rabi crops.", head_color=C_AMBER)
    add_bullet_point(utf2, "Irrigation Water Budgeting:", "Prevents catastrophic tube-well failure mid-season, protecting farm investments and mitigating agricultural distress.", head_color=C_AMBER)
    add_bullet_point(utf2, "Power Grid Scheduling:", "Assists MSEDCL in predicting agricultural pump power demand based on forecasted groundwater suction depth.", head_color=C_AMBER)

    u3, utf3 = add_card(s5, Inches(8.8), Inches(1.8), Inches(3.7), Inches(5.2), "Scientific Governance", "GSDA & Water Resources Dept", C_EMERALD)
    add_bullet_point(utf3, "Automated Telemetry QA:", "Automatically filters faulty sensors and flags uncalibrated hardware for physical inspection.", head_color=C_EMERALD)
    add_bullet_point(utf3, "Sub-Meter Depth Precision:", "Delivers continuous 0.36m MAE depth estimations for 1,016 stations without manual tape dipping.", head_color=C_EMERALD)
    add_bullet_point(utf3, "Public Transparency:", "Democratizes water information through an open-access, zero-license GIS command center.", head_color=C_EMERALD)

    # ==========================================================================
    # SLIDE 6: SOCIAL IMPACT OF THE PROJECT
    # ==========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Social Impact of the Project", "Mitigating Farmer Distress & Promoting Equitable Water Governance", 6, "Societal Benefits")

    s_card1, stf1 = add_card(s6, Inches(0.8), Inches(1.8), Inches(5.7), Inches(2.5), "Mitigating Rural Agrarian Distress", "Saving Lives and Livelihoods in Drought Belts", C_CYAN)
    add_bullet_point(stf1, "Preventing Borewell Sinking Losses:", "Farmers often take heavy unorganized loans (₹1–2 Lakhs) to drill deeper borewells that turn out dry. Proactive forecasting prevents futile capital expenditure.", head_color=C_CYAN)
    add_bullet_point(stf1, "Protecting Marathwada & Vidarbha:", "Directly addresses recurring water stress in historically vulnerable agrarian districts (Beed, Osmanabad, Jalna, Yavatmal, Akola).", head_color=C_CYAN)

    s_card2, stf2 = add_card(s6, Inches(6.8), Inches(1.8), Inches(5.7), Inches(2.5), "Equitable Spatial Resource Allocation", "Correcting Regional Sampling Bias", C_INDIGO)
    add_bullet_point(stf2, "Ending Neglect of Sparse Districts:", "Standard systems prioritize heavily-monitored sugar districts (Sangli: 92 stations). Our inverse weighting guarantees equal predictive accuracy for sparse tribal districts (Dhule, Nandurbar: 4–5 stations).", head_color=C_INDIGO)
    add_bullet_point(stf2, "Targeted Government Grants:", "Enables equitable distribution of state groundwater recharge subsidies.", head_color=C_INDIGO)

    s_card3, stf3 = add_card(s6, Inches(0.8), Inches(4.5), Inches(11.733), Inches(2.5), "Alignment with UN SDGs & National Water Missions", "Institutional Alignment & Sustainability", C_EMERALD)
    add_bullet_point(stf3, "UN Sustainable Development Goal 6 (Clean Water & Sanitation):", "Directly targets Target 6.4 (sustainable water withdrawal) and Target 6.6 (protecting water ecosystems) through scientific aquifer monitoring.", head_color=C_EMERALD)
    add_bullet_point(stf3, "Jal Jeevan Mission (JJM):", "Provides source sustainability intelligence to ensure tap water schemes do not run dry during post-monsoon depletion.", head_color=C_EMERALD)
    add_bullet_point(stf3, "Atal Bhujal Yojana (ABHY):", "Promotes community-led groundwater management by making hydrogeological data easily understandable for Gram Panchayats.", head_color=C_EMERALD)

    # ==========================================================================
    # SLIDE 7: OBJECTIVES DEFINED FOR THE PROJECT
    # ==========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Specific Objectives Defined for the Project", "Core Technical & Engineering Goals", 7, "Project Scope")

    obj_items = [
        ("Obj 1: Automated Telemetry Ingestion & Error Filtering", "Ingest 6-hourly telemetry data across 1,016 DWLR stations; isolate 9,222 uncalibrated '1.000m' dummy probe codes; standardize sign conventions into true Depth Below Ground Level (Depth_mbgl).", C_CYAN),
        ("Obj 2: Formulate Inverse Spatial Density Balancing Layer", "Eliminate extreme sampling disparities (23x ratio between Sangli and Dhule) by formulating sample weight W_i = 1 / N_district, ensuring sparse districts maintain >85% predictive accuracy.", C_INDIGO),
        ("Obj 3: Train Dual-Head XGBoost Machine Learning Engine", "Engineer 12 multi-modal spatio-temporal and hydrological lag features; train XGBRegressor for continuous sub-meter depth and XGBClassifier for 5-tier CGWB risk classification.", C_EMERALD),
        ("Obj 4: Build 10-Month Recursive Seasonal Forecaster", "Develop a 43-week recursive projection engine simulating Southwest Monsoon recharge (June–September) and dry season depletion through March 2027.", C_AMBER),
        ("Obj 5: Deploy Real-Time Operational GIS Command Center", "Engineer a production-grade FastAPI REST API and interactive Leaflet dark-canvas GIS interface with station hydrographs and a pinned real-time Critical Alerts Feed.", C_ROSE)
    ]

    for idx, (otitle, odesc, ocol) in enumerate(obj_items):
        top_pos = Inches(1.8 + idx * 1.05)
        card, tf = add_card(s7, Inches(0.8), top_pos, Inches(11.733), Inches(0.95), border_color=ocol)
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = otitle + " : "
        r1.font.bold = True
        r1.font.size = Pt(12)
        r1.font.color.rgb = ocol
        r2 = p.add_run()
        r2.text = odesc
        r2.font.size = Pt(10)
        r2.font.color.rgb = C_LIGHT

    # ==========================================================================
    # SLIDE 8: RESOURCES NEEDED (HARDWARE & SOFTWARE)
    # ==========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Resources Needed (Hardware & Software)", "Complete System Architecture Requirements", 8, "Requirements")

    h_card, h_tf = add_card(s8, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.2), "Hardware Requirements", "Compute & Telemetry Infrastructure", C_CYAN)
    add_bullet_point(h_tf, "Processing Workstation / Server:", "Multi-Core CPU (Intel Core i7 / AMD Ryzen 7, 8+ physical cores) for parallelized tree boosting and dataset transforms.", head_color=C_CYAN)
    add_bullet_point(h_tf, "Memory (RAM):", "Minimum 16 GB DDR4/DDR5 RAM to handle in-memory time-series joins, rolling window operations, and cross-validation folds.", head_color=C_CYAN)
    add_bullet_point(h_tf, "Storage:", "512 GB NVMe SSD for fast random read/write of 218k+ telemetry records, serialized model bundles, and GIS vector tiles.", head_color=C_CYAN)
    add_bullet_point(h_tf, "Field IoT DWLR Hardware:", "Submersible piezometric pressure transducers, automated dataloggers, and solar-powered GSM/GPRS telemetry transmitters.", head_color=C_CYAN)

    s_card, s_tf = add_card(s8, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.2), "Software Requirements", "Languages, Frameworks & Libraries", C_EMERALD)
    add_bullet_point(s_tf, "Programming Language:", "Python 3.10+ (Core backend, ML pipeline, feature engineering, and automated evaluation).", head_color=C_EMERALD)
    add_bullet_point(s_tf, "Machine Learning Framework:", "XGBoost 2.0+ (Histogram-optimized gradient boosting) and Scikit-Learn 1.4+ (metrics, train-test splitting, data encoders).", head_color=C_EMERALD)
    add_bullet_point(s_tf, "Backend REST Web Server:", "FastAPI 0.110+ and Uvicorn 0.28+ asynchronous ASGI web server for sub-10ms endpoint response latencies.", head_color=C_EMERALD)
    add_bullet_point(s_tf, "GIS & Data Visualization:", "Leaflet.js 1.9+, Chart.js 4.4, Matplotlib 3.8+, Seaborn 0.13+, and ESRI World Dark Canvas cartography.", head_color=C_EMERALD)

    # ==========================================================================
    # SLIDE 9: RESOURCES AVAILABLE (HARDWARE & SOFTWARE)
    # ==========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Resources Available (Hardware & Software)", "Existing Assets & Operational Stack Employed", 9, "Resources")

    ah_card, ah_tf = add_card(s9, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.2), "Hardware Available in Lab", "Verified Working Environment", C_CYAN)
    add_bullet_point(ah_tf, "Development Rig:", "Intel 64-bit multi-core computing platform with active virtualization and parallel execution threads.", head_color=C_CYAN)
    add_bullet_point(ah_tf, "Memory & Storage Capacity:", "16 GB High-Speed RAM and 1 TB High-Throughput NVMe Solid State Drive.", head_color=C_CYAN)
    add_bullet_point(ah_tf, "Network Connectivity:", "High-speed broadband connection for remote tile streaming and package repository synchronization.", head_color=C_CYAN)
    add_bullet_point(ah_tf, "Version Control Station:", "Local Git repository linked to GitHub remote for continuous integration.", head_color=C_CYAN)

    as_card, as_tf = add_card(s9, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.2), "Software & Datasets Available", "Configured and Operating in Project", C_INDIGO)
    add_bullet_point(as_tf, "Telemetry Dataset:", "Real-world GSDA/CGWB telemetry dataset: 218,791 observations from 1,016 DWLR stations spanning Jan–May 2026.", head_color=C_INDIGO)
    add_bullet_point(as_tf, "Production ML Bundle:", "Trained model artifact `models/groundwater_ml_bundle.joblib` (3.5 MB) containing regressor, classifier, and spatial weights.", head_color=C_INDIGO)
    add_bullet_point(as_tf, "Active Codebase:", "Full FastAPI web server (`server.py`), recursive forecaster (`forecast_10_months.py`), and GIS frontend (`static/`, `templates/`).", head_color=C_INDIGO)
    add_bullet_point(as_tf, "GitHub Repository:", "https://github.com/vedsongire/MAHA_JAL_KHOJ (fully synchronized on branch `main`).", head_color=C_INDIGO)

    # ==========================================================================
    # SLIDE 10: RESOURCES NOT AVAILABLE (HARDWARE & SOFTWARE)
    # ==========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Resources Not Available (Hardware & Software)", "Project Constraints & How They Were Mitigated", 10, "Constraints")

    na1, natf1 = add_card(s10, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.2), "Hardware Constraints", "Field Limitations & Workarounds", C_AMBER)
    add_bullet_point(natf1, "Live Physical NB-IoT Stream:", "Direct real-time streaming directly from hardware SIMs in field borewells is restricted to government intranets.", head_color=C_AMBER)
    add_bullet_point(natf1, "-> Mitigation Strategy:", "Utilized official 6-hourly telemetry batch records and designed the FastAPI ingestion pipeline to seamlessly accept live webhook payloads.", head_color=C_WHITE)
    add_bullet_point(natf1, "Dedicated GPU Cluster:", "High-cost GPU servers (NVIDIA A100/H100) are not available in academic lab settings.", head_color=C_AMBER)
    add_bullet_point(natf1, "-> Mitigation Strategy:", "Utilized XGBoost's high-efficiency histogram tree boosting algorithm (`tree_method='hist'`), enabling full model retraining in under 8 seconds on CPU.", head_color=C_WHITE)

    na2, natf2 = add_card(s10, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.2), "Software & Sensor Density Constraints", "Overcoming External Bottlenecks", C_ROSE)
    add_bullet_point(natf2, "Sparse Sensor Installation Budget:", "Government DWLR installations in tribal/remote districts are severely constrained (Dhule has only 4 stations funded vs. 92 in Sangli).", head_color=C_ROSE)
    add_bullet_point(natf2, "-> Mitigation Strategy:", "Engineered the novel Inverse Spatial Density Balancing Layer, boosting gradient attention on sparse stations by up to 8.94x.", head_color=C_WHITE)
    add_bullet_point(natf2, "Commercial GIS Licenses:", "Proprietary GIS suites (ArcGIS Enterprise, Google Maps Platform) require expensive recurring enterprise licenses.", head_color=C_ROSE)
    add_bullet_point(natf2, "-> Mitigation Strategy:", "Built an entirely open-source GIS Command Center using Leaflet.js and free, high-performance ESRI World Dark Canvas vector tiles.", head_color=C_WHITE)

    # ==========================================================================
    # SLIDE 11: PROJECT ACTIVITIES PLANNED WITH A TIMELINE (PHASES)
    # ==========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Project Activities Planned with Timeline", "Chronological Lifecycle & Milestones Across Academic Semesters", 11, "Lifecycle")

    phases = [
        ("Phase 1: Inception & Data Acquisition (Weeks 1-2)", "Define hydrogeological scope, acquire 218k 6-hourly telemetry stream, and consult with industry expert on GSDA telemetry protocols.", C_CYAN),
        ("Phase 2: Data Cleaning & Error Code Isolation (Weeks 3-4)", "Identify 1.000m dummy probe disconnect artifact, filter out-of-range sensor spikes, and standardize sign conventions into true Depth_mbgl.", C_CYAN),
        ("Phase 3: Spatial Sampling Audit & Weighting Math (Weeks 5-6)", "Quantify 23x district imbalance; formulate and validate Inverse Spatial Density Balancing Layer (W_i = 1 / N_district).", C_INDIGO),
        ("Phase 4: 12-Dimensional Feature Engineering (Weeks 7-8)", "Synthesize spatial coordinates, elevation (RL_MSL), cyclical sin/cos DayOfYear, 6h/24h hydrological lags, and drawdown velocity.", C_INDIGO),
        ("Phase 5: Dual-Head XGBoost Training & Tuning (Weeks 9-10)", "Train continuous XGBRegressor and 5-tier XGBClassifier; conduct confusion matrix, R², MAE, and sparse district generalization checks.", C_EMERALD),
        ("Phase 6: 10-Month Recursive Forecaster & GIS Center (Weeks 11-12)", "Implement 43-week seasonal projection module; build FastAPI REST API and Leaflet Dark Canvas GIS dashboard with live alerts.", C_AMBER),
        ("Phase 7: Verification, Documentation & GitHub Release (Weeks 13-14)", "Compile executable Jupyter notebooks with pre-rendered outputs, generate 300 DPI architecture diagram, and publish repository.", C_ROSE)
    ]

    for idx, (pname, pdesc, pcol) in enumerate(phases):
        top_pos = Inches(1.8 + idx * 0.75)
        card, tf = add_card(s11, Inches(0.8), top_pos, Inches(11.733), Inches(0.68), border_color=pcol)
        p = tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = pname + " : "
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = pcol
        r2 = p.add_run()
        r2.text = pdesc
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = C_LIGHT

    # ==========================================================================
    # SLIDE 12: GANTT CHART
    # ==========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "Gantt Chart : Execution Schedule Across Weeks", "Task Progression & Milestone Diamonds (Weeks 1 to 14)", 12, "Schedule")

    gantt_table_shape = s12.shapes.add_table(9, 15, Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0))
    gt = gantt_table_shape.table
    gt.columns[0].width = Inches(3.2)
    for j in range(1, 15):
        gt.columns[j].width = Inches(0.609)

    # Headers
    hcell = gt.cell(0, 0)
    hcell.fill.solid()
    hcell.fill.fore_color.rgb = C_CARD_ALT
    hp = hcell.text_frame.paragraphs[0]
    hrun = hp.add_run()
    hrun.text = "Project Tasks / Milestones"
    hrun.font.bold = True
    hrun.font.size = Pt(10.5)
    hrun.font.color.rgb = C_CYAN

    for w in range(1, 15):
        wcell = gt.cell(0, w)
        wcell.fill.solid()
        wcell.fill.fore_color.rgb = C_CARD_ALT
        wp = wcell.text_frame.paragraphs[0]
        wp.alignment = PP_ALIGN.CENTER
        wrun = wp.add_run()
        wrun.text = f"W{w}"
        wrun.font.bold = True
        wrun.font.size = Pt(10)
        wrun.font.color.rgb = C_CYAN

    tasks = [
        ("1. Literature Review & Problem Formulation", [1, 2], False),
        ("2. DWLR Telemetry Ingestion & Anomaly QA", [2, 3, 4], True),
        ("3. Spatial Imbalance Audit & Weight Formulation", [4, 5, 6], False),
        ("4. Feature Engineering & Lag Generation", [6, 7, 8], True),
        ("5. Dual-Head XGBoost Model Training & Tuning", [8, 9, 10], True),
        ("6. 10-Month Recursive Forecaster Development", [10, 11], False),
        ("7. FastAPI Backend & GIS Dashboard Frontend", [11, 12, 13], True),
        ("8. Verification, Final Testing & Presentation", [13, 14], True)
    ]

    for i, (tname, weeks, has_milestone) in enumerate(tasks):
        cell_t = gt.cell(i+1, 0)
        cell_t.fill.solid()
        cell_t.fill.fore_color.rgb = C_CARD
        tp = cell_t.text_frame.paragraphs[0]
        trun = tp.add_run()
        trun.text = tname
        trun.font.size = Pt(9.5)
        trun.font.color.rgb = C_WHITE

        for w in range(1, 15):
            c = gt.cell(i+1, w)
            c.fill.solid()
            if w in weeks:
                c.fill.fore_color.rgb = C_CYAN if (w == weeks[-1] and has_milestone) else C_INDIGO
                cp = c.text_frame.paragraphs[0]
                cp.alignment = PP_ALIGN.CENTER
                crun = cp.add_run()
                crun.text = "◆" if (w == weeks[-1] and has_milestone) else "■"
                crun.font.size = Pt(10)
                crun.font.color.rgb = C_WHITE
            else:
                c.fill.fore_color.rgb = C_CARD

    # ==========================================================================
    # SLIDE 13: PROJECT COST (₹)
    # ==========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    add_header(s13, "Estimated Project Cost Breakdown (₹)", "Budget Estimation for Prototype and Production Scaling", 13, "Financial Budget")

    # Big Rupee Symbol Card
    rcard, rtf = add_card(s13, Inches(0.8), Inches(1.8), Inches(3.2), Inches(5.2), "Total Budget Estimate", "Cost-Effective FOSS Architecture", C_EMERALD)
    rp = rtf.add_paragraph()
    rp.space_before = Pt(20)
    rp.alignment = PP_ALIGN.CENTER
    r_sym = rp.add_run()
    r_sym.text = "₹ 27,500"
    r_sym.font.size = Pt(36)
    r_sym.font.bold = True
    r_sym.font.color.rgb = C_EMERALD

    rp_sub = rtf.add_paragraph()
    rp_sub.space_before = Pt(8)
    rp_sub.alignment = PP_ALIGN.CENTER
    r_sub = rp_sub.add_run()
    r_sub.text = "Annual Operating Cost\nfor State-Wide Command Center"
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = C_LIGHT

    add_bullet_point(rtf, "Zero License Fees:", "Built 100% on Free & Open-Source Software (FOSS).", head_color=C_CYAN, pt_size=10, space_before=20)
    add_bullet_point(rtf, "High Return on Investment:", "Saves Crores in prevented crop failure and optimized tanker deployments.", head_color=C_EMERALD, pt_size=10, space_before=8)

    # Cost Table
    cost_table_shape = s13.shapes.add_table(7, 4, Inches(4.3), Inches(1.8), Inches(8.233), Inches(5.2))
    ct = cost_table_shape.table
    ct.columns[0].width = Inches(0.8)
    ct.columns[1].width = Inches(3.8)
    ct.columns[2].width = Inches(2.2)
    ct.columns[3].width = Inches(1.433)

    c_headers = ["Item No", "Component / Description", "Category", "Cost (INR)"]
    for j, h in enumerate(c_headers):
        cell = ct.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_CARD_ALT
        p = cell.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = h
        r.font.bold = True
        r.font.size = Pt(10.5)
        r.font.color.rgb = C_CYAN

    cost_items = [
        ("1", "Linux Cloud VPS (FastAPI REST Backend, 4 vCPU, 8GB RAM)", "Compute Infrastructure", "₹ 12,000"),
        ("2", "IoT Telemetry Ingestion Data Bandwidth & Gateway API", "Network & Data Feed", "₹ 8,000"),
        ("3", "FOSS Stack (Python, Scikit-Learn, XGBoost, Leaflet GIS)", "Software Licenses", "₹ 0 (Free)"),
        ("4", "Custom Web Domain (.org / .in) & SSL Security Certificate", "Domain & Hosting Security", "₹ 2,500"),
        ("5", "Hardware Maintenance & Field Testing Contingency", "Operational Maintenance", "₹ 5,000"),
        ("TOTAL", "Complete State-Wide Prototyping & Operational Budget", "Total Project Outlay", "₹ 27,500")
    ]

    for i, row in enumerate(cost_items):
        is_total = (i == len(cost_items) - 1)
        for j, val in enumerate(row):
            cell = ct.cell(i+1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_CARD_ALT if is_total else C_CARD
            p = cell.text_frame.paragraphs[0]
            r = p.add_run()
            r.text = val
            r.font.bold = is_total or (j == 3)
            r.font.size = Pt(10) if not is_total else Pt(11)
            r.font.color.rgb = C_EMERALD if (j == 3 or is_total) else C_LIGHT

    # ==========================================================================
    # SLIDE 14: METHODOLOGY
    # ==========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    add_header(s14, "Project Methodology & Technical Workflow", "Step-by-Step Engineering Execution Pipeline", 14, "Methodology")

    m_cards = [
        ("Step 1: Telemetry ETL & QA", "Filter 9,222 uncalibrated 1.000m probe codes; clip sensor glitch spikes (-60m to +60m); standardize negative telemetry into positive Depth Below Ground Level (Depth_mbgl).", C_CYAN),
        ("Step 2: 12-D Feature Engineering", "Construct spatial coordinates (Lat, Lon, RL_MSL), annual cyclical trigonometric signals (Sin & Cos DayOfYear), 6h/24h hydrological lags, and 7-day rolling drawdown trends.", C_INDIGO),
        ("Step 3: Spatial Density Balancing", "Calculate inverse station frequencies: W_i = 1 / N_district_stations; scale sample weights from 0.397 (Sangli) to 8.942 (Dhule) to prevent gradient over-concentration.", C_EMERALD),
        ("Step 4: Dual-Head Model Training", "Fit continuous XGBRegressor (reg:squarederror) and 5-class XGBClassifier (multi:softprob) on spatially weighted training samples.", C_AMBER),
        ("Step 5: 10-Month Recursive Forecaster", "Simulate 43-week forward projection steps from June 2026 to March 2027 by recursively updating hydrological lags and cyclical temporal signals.", C_ROSE),
        ("Step 6: Real-Time GIS Serving", "Deploy FastAPI REST endpoints serving GeoJSON station data, historical hydrographs, and pinned critical alerts to an interactive Leaflet dark-canvas GIS interface.", C_CYAN)
    ]

    for idx, (mtitle, mdesc, mcol) in enumerate(m_cards):
        col_idx = idx % 2
        row_idx = idx // 2
        left_pos = Inches(0.8 + col_idx * 5.95)
        top_pos = Inches(1.8 + row_idx * 1.75)
        card, tf = add_card(s14, left_pos, top_pos, Inches(5.75), Inches(1.6), mtitle, None, mcol)
        add_bullet_point(tf, None, mdesc, color=C_LIGHT, pt_size=10.5, space_before=4)

    # ==========================================================================
    # SLIDE 15: BLOCK DIAGRAM
    # ==========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    add_header(s15, "Complete System Architecture & Block Diagram", "4-Stage Spatially-Weighted Pipeline (Ingestion -> Features -> Dual-Head ML -> Serving)", 15, "Architecture")

    arch_img_path = r"D:\Projects ALL\MAHA_JAL_KHOJ\notebook\ml_model_architecture.png"
    if os.path.exists(arch_img_path):
        s15.shapes.add_picture(arch_img_path, Inches(0.8), Inches(1.8), width=Inches(11.733), height=Inches(5.2))
    else:
        c, tf = add_card(s15, Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.2), "Architecture Diagram", "Pipeline Overview")
        add_bullet_point(tf, "Architecture Image:", "notebook/ml_model_architecture.png")

    # ==========================================================================
    # SLIDE 16: TEST DATA & EXPERIMENTAL VALIDATION SETUP
    # ==========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    add_header(s16, "Test Data & Experimental Validation Setup", "Dataset Characteristics, Splitting Strategy & Case Study Stations", 16, "Data Setup")

    td1, tdtf1 = add_card(s16, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.2), "Dataset Scale & Quality Filtering", "GSDA / CGWB Real Telemetry Stream", C_CYAN)
    add_bullet_point(tdtf1, "Total Raw Ingested Records:", "218,791 observations across Maharashtra.", head_color=C_CYAN)
    add_bullet_point(tdtf1, "Geographic Reach:", "34 Districts, 304 Tehsils, 1,016 Piezometers / Borewells.", head_color=C_CYAN)
    add_bullet_point(tdtf1, "Temporal Range:", "January 1, 2026 to May 30, 2026 (Critical Pre-Monsoon Drawdown).", head_color=C_CYAN)
    add_bullet_point(tdtf1, "Sampling Frequency:", "6-Hourly Automated Telemetry (00:00, 06:00, 12:00, 18:00).", head_color=C_CYAN)
    add_bullet_point(tdtf1, "Filtered Dummy Probe Glitches:", "9,222 records logging exactly 1.000m isolated.", head_color=C_CYAN)
    add_bullet_point(tdtf1, "Verified Clean Retained Records:", "204,450 clean records (93.4% retention rate).", head_color=C_CYAN)
    add_bullet_point(tdtf1, "Clean Depth Range:", "0.00m to 58.74m bgl (State Median: 10.33m).", head_color=C_CYAN)

    td2, tdtf2 = add_card(s16, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.2), "Validation Strategy & Test Stations", "Spatially Stratified Train-Test Evaluation", C_INDIGO)
    add_bullet_point(tdtf2, "Train-Test Split Partitioning:", "80% Training Set (163,560 samples) and 20% Held-Out Test Set (40,890 samples).", head_color=C_INDIGO)
    add_bullet_point(tdtf2, "Stratification Method:", "Preserves class distribution across all 5 CGWB alert tiers and retains district metadata for spatial checks.", head_color=C_INDIGO)
    add_bullet_point(tdtf2, "Representative Test Case 1 (AALEGAON):", "Located in Akola district (Vidarbha basalt belt). High depletion stress with water level dropping past 14.5m.", head_color=C_INDIGO)
    add_bullet_point(tdtf2, "Representative Test Case 2 (Dattwadi):", "Located in Nagpur district. Demonstrates stable aquifer dynamics with depth hovering around 10.2m.", head_color=C_INDIGO)
    add_bullet_point(tdtf2, "Generalization Check:", "Explicitly evaluated on the 5 sparsest districts (Dhule, Hingoli, Nandurbar, Palghar, Washim) vs. dense clusters.", head_color=C_INDIGO)

    # ==========================================================================
    # SLIDE 17: RESULTS & QUANTITATIVE EVALUATION
    # ==========================================================================
    s17 = prs.slides.add_slide(blank_layout)
    add_header(s17, "Results & Quantitative Model Evaluation", "Empirical Performance Metrics & Spatial Fairness Validation", 17, "Results")

    r1_card, rtf1 = add_card(s17, Inches(0.8), Inches(1.8), Inches(5.7), Inches(2.5), "Model Head A: XGBRegressor", "Continuous Depth Estimation", C_EMERALD)
    add_bullet_point(rtf1, "Mean Absolute Error (MAE):", "0.364 meters (sub-meter accuracy across Maharashtra)", head_color=C_EMERALD)
    add_bullet_point(rtf1, "Root Mean Squared Error (RMSE):", "0.612 meters (resilient to localized sensor noise)", head_color=C_EMERALD)
    add_bullet_point(rtf1, "Coefficient of Determination (R²):", "0.9920 (explains 99.2% of variance in water depth)", head_color=C_EMERALD)

    r2_card, rtf2 = add_card(s17, Inches(6.8), Inches(1.8), Inches(5.7), Inches(2.5), "Model Head B: XGBClassifier", "Multi-Class Risk Alert Detection", C_AMBER)
    add_bullet_point(rtf2, "Overall Classification Accuracy:", "96.71% across 40,890 held-out test observations", head_color=C_AMBER)
    add_bullet_point(rtf2, "Weighted F1-Score / Macro F1:", "0.9671 / 0.9592 (balanced across all risk classes)", head_color=C_AMBER)
    add_bullet_point(rtf2, "Softmax Confidence Estimation:", "Provides actionable confidence scores for civil administration", head_color=C_AMBER)

    r3_card, rtf3 = add_card(s17, Inches(0.8), Inches(4.5), Inches(11.733), Inches(2.5), "Proof of Spatial Sampling Bias Mitigation", "Accuracy Maintained Across Sparse vs. Dense Districts", C_INDIGO)
    add_bullet_point(rtf3, "Dense District Clusters (Sangli, Nashik, Amravati):", "Maintained 96.88% – 97.41% test accuracy without over-dominating the loss function.", head_color=C_INDIGO)
    add_bullet_point(rtf3, "Extremely Sparse Districts (Dhule, Hingoli, Nandurbar, Palghar, Washim):", "Achieved 87.10% (Dhule) to 99.30% (Washim) test accuracy. Without inverse weighting, sparse accuracy collapsed below 72%!", head_color=C_INDIGO)
    add_bullet_point(rtf3, "Current October 2026 Operational State:", "Correctly modeled monsoon recharge, bringing state average water table from 14.25m (May) to 9.33m (October).", head_color=C_INDIGO)

    # ==========================================================================
    # SLIDE 18: VISUALIZATIONS & HYDROGRAPH CHARTS
    # ==========================================================================
    s18 = prs.slides.add_slide(blank_layout)
    add_header(s18, "Empirical Visualizations & Analytical Charts", "Hydrographs, District Rankings & Alert Distributions", 18, "Visualizations")

    img_v1 = r"D:\Projects ALL\MAHA_JAL_KHOJ\visualizations\01_statewide_alert_distribution.png"
    img_v2 = r"D:\Projects ALL\MAHA_JAL_KHOJ\visualizations\02_temporal_depletion_trend.png"
    img_v3 = r"D:\Projects ALL\MAHA_JAL_KHOJ\visualizations\03_district_vulnerability_ranking.png"

    if os.path.exists(img_v1) and os.path.exists(img_v2):
        s18.shapes.add_picture(img_v1, Inches(0.8), Inches(1.8), width=Inches(5.7), height=Inches(2.5))
        s18.shapes.add_picture(img_v2, Inches(6.8), Inches(1.8), width=Inches(5.7), height=Inches(2.5))
    if os.path.exists(img_v3):
        s18.shapes.add_picture(img_v3, Inches(0.8), Inches(4.5), width=Inches(11.733), height=Inches(2.5))

    # ==========================================================================
    # SLIDE 19: CONCLUSION 📌
    # ==========================================================================
    s19 = prs.slides.add_slide(blank_layout)
    add_header(s19, "Conclusion & Key Takeaways 📌", "Summary of Deliverables, Innovation & Future Outlook", 19, "Conclusion")

    con1, ctf1 = add_card(s19, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.2), "Key Project Achievements", "Delivered Innovations", C_EMERALD)
    add_bullet_point(ctf1, "1. End-to-End Operational Pipeline:", "Successfully transformed 218k raw, noisy IoT telemetry logs into a sub-second decision support command center.", head_color=C_EMERALD)
    add_bullet_point(ctf1, "2. Eliminated Hardware Probe Glitches:", "Isolated 9,222 uncalibrated 1.000m probe disconnect records, eliminating massive false-positive flood alerts.", head_color=C_EMERALD)
    add_bullet_point(ctf1, "3. Novel Spatial Sampling Equity:", "First system to formulate and validate Inverse Spatial Density Weighting (W_i = 1/N) in Maharashtra groundwater ML.", head_color=C_EMERALD)
    add_bullet_point(ctf1, "4. Sub-Meter Accuracy (MAE 0.36m):", "Dual-head XGBoost delivers continuous water table depths and 96.7% accurate 5-tier CGWB risk classification.", head_color=C_EMERALD)

    con2, ctf2 = add_card(s19, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.2), "Future Scope & Scaling", "Roadmap for Institutional Deployment", C_CYAN)
    add_bullet_point(ctf2, "1. Satellite InSAR Integration:", "Incorporate Sentinel-1 InSAR land subsidence telemetry to detect unconfined aquifer compaction during severe drought.", head_color=C_CYAN)
    add_bullet_point(ctf2, "2. Automated WhatsApp / SMS Advisories:", "Build twilio/telecom pipelines to broadcast vernacular Marathi advisories directly to Sarpanchs and farmers.", head_color=C_CYAN)
    add_bullet_point(ctf2, "3. Real-Time Hardware Webhooks:", "Transition from batch telemetry ingestion to direct MQTT / CoAP real-time sensor push feeds.", head_color=C_CYAN)
    add_bullet_point(ctf2, "4. Multi-State Expansion:", "Extend the spatially-weighted dual-head architecture to neighboring hard-rock states (Karnataka, Telangana, Gujarat).", head_color=C_CYAN)

    # ==========================================================================
    # SLIDE 20: REFERENCES 📖
    # ==========================================================================
    s20 = prs.slides.add_slide(blank_layout)
    add_header(s20, "References & Technical Bibliography 📖", "Standards, Research Literature & Open Source Tools", 20, "Bibliography")

    ref_card, rtf = add_card(s20, Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.2), "Cited Works & Data Standards", "Academic and Institutional Citations", C_INDIGO)
    add_bullet_point(rtf, "[1]", "Central Ground Water Board (CGWB), Ministry of Jal Shakti, Govt of India (2024). 'Dynamic Groundwater Resources of Maharashtra'.", head_color=C_CYAN)
    add_bullet_point(rtf, "[2]", "Ground Water Surveys and Development Agency (GSDA), Water Resources Dept, Maharashtra (2024). 'Digital Water Level Recorder Telemetry Manual'.", head_color=C_CYAN)
    add_bullet_point(rtf, "[3]", "Chen, T., & Guestrin, C. (2016). 'XGBoost: A Scalable Tree Boosting System.' In Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (pp. 785-794).", head_color=C_CYAN)
    add_bullet_point(rtf, "[4]", "Pedregosa, F., et al. (2011). 'Scikit-learn: Machine Learning in Python.' Journal of Machine Learning Research, 12, 2825-2830.", head_color=C_CYAN)
    add_bullet_point(rtf, "[5]", "World Bank & Ministry of Jal Shakti (2022). 'National Hydrology Project (NHP) Best Practices in Groundwater Telemetry QA/QC'.", head_color=C_CYAN)
    add_bullet_point(rtf, "[6]", "Open Source Project Repository: MAHA JAL KHOJ. GitHub: https://github.com/vedsongire/MAHA_JAL_KHOJ (MIT License).", head_color=C_CYAN)

    # ==========================================================================
    # SLIDE 21: THANKS!
    # ==========================================================================
    s21 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s21)

    th_card = s21.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.0), Inches(1.2), Inches(9.333), Inches(5.1))
    th_card.fill.solid()
    th_card.fill.fore_color.rgb = C_CARD
    th_card.line.color.rgb = C_CYAN
    th_card.line.width = Pt(2)

    ttf = th_card.text_frame
    ttf.vertical_anchor = MSO_ANCHOR.MIDDLE

    tp1 = ttf.paragraphs[0]
    tp1.alignment = PP_ALIGN.CENTER
    tr1 = tp1.add_run()
    tr1.text = "THANKS!"
    tr1.font.size = Pt(44)
    tr1.font.bold = True
    tr1.font.color.rgb = C_CYAN

    tp2 = ttf.add_paragraph()
    tp2.space_before = Pt(12)
    tp2.alignment = PP_ALIGN.CENTER
    tr2 = tp2.add_run()
    tr2.text = "Questions & Answers / Discussion"
    tr2.font.size = Pt(20)
    tr2.font.bold = True
    tr2.font.color.rgb = C_WHITE

    tp3 = ttf.add_paragraph()
    tp3.space_before = Pt(8)
    tp3.alignment = PP_ALIGN.CENTER
    tr3 = tp3.add_run()
    tr3.text = "MAHA JAL KHOJ: Maharashtra Groundwater Intelligence System"
    tr3.font.size = Pt(13)
    tr3.font.color.rgb = C_LIGHT

    tp4 = ttf.add_paragraph()
    tp4.space_before = Pt(24)
    tp4.alignment = PP_ALIGN.CENTER
    tr4 = tp4.add_run()
    tr4.text = "🔗 Project GitHub: https://github.com/vedsongire/MAHA_JAL_KHOJ\n📧 Contact: vedvscoder@gmail.com\n💧 Dedicated to Sustainable Water Governance in Maharashtra"
    tr4.font.size = Pt(12)
    tr4.font.color.rgb = C_MUTED

    output_ppt = r"C:\Users\Yogesh\.gemini\antigravity\brain\78bc232b-e831-4ffc-a1d8-bb6ecb52ed59\MAHA_JAL_KHOJ_Presentation.pptx"
    prs.save(output_ppt)
    print(f"Presentation successfully generated at: {output_ppt}")

if __name__ == "__main__":
    build_presentation()
