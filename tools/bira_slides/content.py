# -*- coding: utf-8 -*-
"""Text content of every slide (transcribed from the screenshots). Card order = reading order (row by row)."""

R = "r"   # regular
B = "b"   # bold

# ---- A (overlay-card) slides: title segments, pill text, cards
# card: {"right": [lines]} | {"left": [[label, value], ...], "above": str} + optional "caption": [lines], "pilltext": str, "topright": str
A = {
    "bfsi2": dict(title=[[("MAJOR ", R, 0), ("BFSI", B, 1), (" PROJECTS", R, 0)]], pill="ACROSS INDIA", cards=[
        dict(right=["Principal Global", "Pune", "3L Sq.ft"]),
        dict(right=["Nomura", "Mumbai", "1,50,000 Sq.ft"]),
        dict(right=["Bank of Newyork Mellon", "Pune", "VRV & FITOUT | 4 L Sq.ft"]),
        dict(right=["BNP Paribas", "Mumbai", "30k sqft"]),
        dict(right=["UBS", "Scope: VRV", "Mumbai, Pune, Hyderabad"]),
        dict(right=["JP Morgan Chase", "Mumbai", "3.5LSq ft"]),
    ]),
    "bfsi3": dict(title=[[("MAJOR ", R, 0), ("BFSI", B, 1), (" PROJECTS", R, 0)]], pill="ACROSS INDIA", cards=[
        dict(right=["BACI", "Chennai, Gujrat, Bangalore,", "Mumbai"]),
        dict(right=["Brookfield", "Mumbai", "1,10,000 Sq ft"]),
        dict(right=["Goldman Sachs", "Mumbai"]),
        dict(right=["HSBC Bangalore", "2,00,000 Sq.ft"]),
        dict(right=["Citi Bank", "Mumbai, Delhi & Chennai", "78,000 Sq.ft"]),
        dict(right=["Mastercard", "1200 TR", "1L Sq. ft.", "Mumbai & Pune"]),
    ]),
    "dcmajor": dict(title=[[("MAJOR DC", B, 0), (" PROJECTS", R, 0)]], pill=None, stats=True, cards=[
        dict(right=["25 MW", "Hyd & Mumbai"], pilltext="Green Field, DC"),
        dict(right=["17 MW", "Pune & Mumbai"]),
        dict(right=["3 MW", "Mumbai"]),
        dict(right=["10 MW", "Mumbai"]),
        dict(right=["3 MW", "Chennai"]),
    ]),
    "edu": dict(title=[[("MAJOR", B, 0), (" PROJECTS", R, 0)]], pill="EDUCATION INSTITUTES", cards=[
        dict(right=["HVAC", "Mumbai"], pilltext="Al Jamea Tus Saifiyah"),
        dict(right=["HVAC", "Hyderabad"]),
        dict(right=["MEP", "Mumbai"]),
        dict(right=["HVAC", "Mumbai"]),
        dict(right=["HVAC", "Bangalore"]),
        dict(right=["HVAC", "Mumbai"]),
    ]),
    "ind": dict(title=[[("MAJOR", B, 0), (" PROJECTS", R, 0)]], pill="INDUSTRIAL + WAREHOUSING", cards=[
        dict(right=["HVAC", "1.6L Sq. Ft.", "Khalapur"]),
        dict(right=["HVAC", "2.25L Sq. Ft.", "Bhiwandi"]),
        dict(right=["HVAC", "1L Sq. Ft.", "Mum, BLR & Delhi NCR"]),
        dict(right=["HVAC", "5L Sq. Ft.", "Jamnagar"]),
        dict(right=["HVAC", "8L Sq. Ft.", "Banglore"]),
        dict(right=["MEP", "61K Sq. Ft.", "Hossur"]),
    ]),
    "mfg": dict(title=[[("PROJECT", B, 0), (" GALLERY", R, 0)]], pill="MANUFACTURING", cards=[
        dict(right=["Banglore"]), dict(right=["Noida"]), dict(right=["Mumbai"]),
        dict(right=["Mumbai"]), dict(right=["Chakan"]), dict(right=["Pune"]),
    ]),
    "res1": dict(title=[[("MAJOR", B, 0), (" PROJECTS", R, 0)]], pill="PRIVATE LUXURY RESIDENTIAL", cards=[
        dict(right=["Ahuja Towers,", "Worli"]),
        dict(right=["Indiabulls Blu,", "Mumbai"]),
        dict(right=["RARE Villa,", "Mumbai"]),
        dict(right=["Jalsa,", "Mumbai"]),
        dict(right=["Hinduja’s", "Bunglow -Lyutens"]),
        dict(right=["Sameer Gehlaut", "PentHouse"]),
    ]),
    "pune1": dict(title=[[("MAJOR", B, 0), (" PROJECTS IN ", R, 0), ("PUNE", B, 0)]], pill="INSTALLED BASE OF 6.5 MILLION SQ. FT.", cards=[
        dict(right=["Electrical", "5L sq.ft.", "Baner & Kharadi"]),
        dict(right=["HVAC", "8.5L Sq.ft."]),
        dict(right=["SCOPE: HVAC Fitout", "AREA:  3L"], topright="Pune"),
        dict(right=["HVAC", "1.5L SQ.FT"]),
        dict(right=["HVAC", "6.75L SQ.FT"]),
        dict(right=["HVAC", "1.75L SQ.FT."]),
    ]),
    "pune3b": dict(title=[[("MAJOR", B, 0), (" PROJECTS IN ", R, 0), ("PUNE", B, 0)]], pill="INSTALLED BASE OF 6.5 MILLION SQ. FT.", cards=[
        dict(right=["HVAC", "50K Sq.ft"]),
        dict(right=["HVAC & FITOUT", "4 L Sq.ft"]),
        dict(right=["HVAC", "Pune"]),
        dict(right=["HVAC", "Mumbai, Pune & Chennai", "3L Sq.ft"]),
        dict(right=["FITOUT", "3.5L Sq.ft", "Koreagoan Park"]),
        dict(right=["HVAC", "1.65L Sq.ft"]),
    ]),
    "pune3": dict(title=[[("MAJOR", B, 0)], [("PROJECTS IN PUNE", R, 0)]], pill="INSTALLED BASE OF 6.5 MILLION SQ. FT.", cards=[
        dict(right=["VRV", "80,000 sq.ft", "Hinjewadi"]),
        dict(right=["Basebuild- CH Water", "4,00,000 sq.ft", "Pune"]),
        dict(right=["Fitout", "40,000 sq.ft", "Pune"]),
        dict(right=["Fitout", "50,000 sq.ft", "Pune"]),
        dict(right=["FITOUT", "90k sq.ft | 3 Phases", "Hinjewadi"]),
        dict(right=["FIT OUT", "1L Sq. ft.", "Pune"]),
    ]),
    "south1": dict(title=[[("MAJOR SOUTH", B, 1), (" PROJECTS", R, 0)]], pill="TAMIL NADU", cards=[
        dict(right=["MEP", "61K Sq. Ft.", "Hossur"]),
        dict(right=["VRV", "3MW", "Chennai"]),
        dict(left=[["AREA:", "4.1L Sq.Ft"], ["SCOPE:", "Fitout"]], caption=["CTS, COIMBATORE", "PHASE 1 & 2"]),
        dict(right=["Fitout", "10K Sq. Ft.", "Chennai"]),
        dict(right=["Fitout", "6L Sq. Ft.", "Chennai"]),
    ]),
    "south2": dict(title=[[("MAJOR BFSI SOUTH", B, 1), (" PROJECTS", R, 0)]], pill="TAMIL NADU", cards=[
        dict(left=[["AREA:", "4 L Sq.Ft."], ["SCOPE:", "Fitout"], ["VALUE:", "12.4 Cr"], ["COMPLETION:", "2024"]]),
        dict(left=[["AREA:", "1 L Sq.Ft."], ["SCOPE:", "HVAC & FF"], ["VALUE:", "5 Cr"], ["COMPLETION:", "2024"]]),
        dict(left=[["AREA:", "100000"], ["SCOPE:", "VRV"]]),
        dict(left=[["AREA:", "55000"], ["SCOPE:", "Fitout"]]),
    ]),
    "south3": dict(title=[[("MAJOR SOUTH", B, 1), (" PROJECTS", R, 0)]], pill="TAMIL NADU", cards=[
        dict(left=[["AREA:", "27350"], ["SCOPE:", "VRV"]], caption=["HIRANANDANI CLUB HOUSE,", "CHENNAI"]),
        dict(left=[["AREA:", "100000"], ["SCOPE:", "Fitout"]], caption=["RMZ FOOD COURT, CHENNAI", "MARKET PLACE"]),
        dict(left=[["AREA:", "50000"], ["SCOPE:", "VRV"]], caption=["LOREAL, CHENNAI"]),
        dict(left=[["AREA:", "18000"], ["SCOPE:", "Fitout"]], caption=["KPMG CHENNAI"]),
    ]),
    "south4": dict(title=[[("MAJOR SOUTH", B, 1), (" PROJECTS", R, 0)]], pill="HYDERABAD", cards=[
        dict(right=["2800 TR", "8.0L Sq. ft.", "HYDERABAD"], pilltext="Phoenix Trivium"),
        dict(right=["HVAC", "11.5L Sq.Ft.", "Bengalore"]),
        dict(right=["HVAC", "2.9L Sq.Ft.", "Hyderabad"]),
        dict(right=["VRV", "30K Sq.Ft", "Hyderabad"]),
        dict(right=["VRV", "40K Sq. Ft.", "Hyderabad"]),
        dict(right=["VRV", "85K Sq. Ft.", "Banagalore & Hyderbad"]),
    ]),
    "south5": dict(title=[[("MAJOR SOUTH", B, 1), (" PROJECTS", R, 0)]], pill="BANGALORE", cards=[
        dict(right=["MEP", "8.0L Sq.Ft.", "Bangalore"]),
        dict(right=["HVAC", "1.5 L Sq.Ft.", "Bangalore"]),
        dict(left=[["VALUE:", "1.5 L"], ["SCOPE:", "Fitout/ HVAC"]], above="LTI Campus, Mysore"),
        dict(right=["Fitout", "80K Sq.Ft.", "Whitefield"]),
        dict(right=["Fitout VRV", "2L Sq.Ft.", "MG Road"]),
    ]),
}

# ---- B (side panel + photos + captions) slides
# card: name, loc, meta [[label, value]...]
Bs = {
    "bfsi1": dict(panel=["MAJOR BFSI", "PROJECTS"], cards=[
        ("Morgan Stanley", "Mumbai", [["AREA:", "1.M"], ["SCOPE:", "Mechanical"]]),
        ("JP Morgan", "Powai, Mumbai", [["AREA:", "3.5L"], ["SCOPE:", "HVAC"]]),
        ("Bank of America", "Mum, Guj, Chennai & BLR", [["AREA:", "0.2 M"], ["SCOPE:", "HVAC"]]),
        ("Goldman Sachs", "Worli, Mumbai", [["AREA:", "40,000"], ["SCOPE:", "HVAC"]]),
        ("Citi Bank", "Mumbai, Pune & Chennai", [["AREA:", "3,00,000"], ["SCOPE:", "HVAC"]]),
        ("Mastercard", "Mumbai, Pune & Vadodara", [["AREA:", "9,00,000"], ["SCOPE:", "HVAC"]]),
        ("HSBC", "Chennai", [["AREA:", "2,00,000"], ["SCOPE:", "HVAC"]]),
        ("IndusInd Bank", "Chennai", [["AREA:", "5,00,000"], ["SCOPE:", "MEP"]]),
    ]),
    "cre1": dict(panel=["MAJOR CRE", "PROJECTS"], cards=[
        ("Principal Global", "Pune", [["AREA:", "3,00,000"], ["SCOPE:", "HVAC"]]),
        ("Dextrus", "BKC, Mumbai", [["AREA:", "-----"], ["SCOPE:", "MEP"]]),
        ("BNP Paribas", "Mumbai", [["AREA:", "30,000"], ["SCOPE:", "HVAC"]]),
        ("BNY Mellon", "Mumbai", [["AREA:", "4,00,000"], ["SCOPE:", "HVAC Fitout"]]),
        ("UBS", "Mumbai, Pune, Hyderabad", [["AREA:", "78,000"], ["SCOPE:", "HVAC"]]),
        ("Legato", "Hyderabad", [["AREA:", "5,00,000"], ["SCOPE:", "HVAC"]]),
        ("Qualcomm", "Bangalore", [["AREA:", "11,50,000"], ["SCOPE:", "HVAC"]]),
        ("WeWork", "Pan India", [["AREA:", "6,00,000"], ["SCOPE:", "HVAC"]]),
    ]),
    "cre2": dict(panel=["MAJOR CRE", "PROJECTS"], cards=[
        ("Netflix", "Mumbai", [["AREA:", "1,50,000"], ["SCOPE:", "HVAC"]]),
        ("Google", "Delhi & Mumbai", [["AREA:", "1,00,000"], ["SCOPE:", "HVAC"]]),
        ("Microsoft", "Hydrabad", [["AREA:", "1,50,000"], ["SCOPE:", "HVAC"]]),
        ("Poonawala", "Pune", [["AREA:", "1,50,000"], ["SCOPE:", "HVAC"]]),
        ("Kotak", "Mumbai", [["AREA:", "3,40,000"], ["SCOPE:", "HVAC"]]),
        ("Crisis House", "Powai", [["AREA:", "5,00,000"], ["SCOPE:", "HVAC"]]),
        ("Times Tower", "Mumbai", [["AREA:", "1,50,000"], ["SCOPE:", "HVAC"]]),
        ("S&P Global", "Gujrat", [["AREA:", "7,50,000"], ["SCOPE:", "HVAC"]]),
    ]),
    "dcnew": dict(panel=["NEW DC", "PROJECTS"], cards=[
        ("ADANI", "Mumbai", [["MW:", "42.8"], ["SCOPE:", "MEP"], ["VALUE:", "52 CRS"]]),
        ("CTRL S", "Navi Mumbai", [["MW:", "24 MW"], ["SCOPE:", "HVAC"], ["VALUE:", "40 CRS"]]),
        ("BOM 10", "Mumbai", [["AREA:", "88k"], ["SCOPE:", "MEP"], ["VALUE:", "25 CRS"]]),
        ("CTRL S", "Hyderabad", [["MW:", "80"], ["SCOPE:", "Fire Fighting & Plumbing"], ["VALUE:", "31 CRS"]]),
    ]),
    "res2": dict(panel=["HIGH RISE"], cards=[
        ("Lotus Builders", "Juhu, Mumbai", [["FLOORS", "16"]]),
        ("Ahuja Towers,", "Worli", [["FLOORS", "55"]]),
        ("India bulls blue", "Mumbai", [["FLOORS", "50"]]),
        ("Lotus Arcadian", "Juhu", [["BUILDINGS:", "2"], ["FLOORS:", "26"]]),
        ("L&T sea woods", "Navi Mumbai", [["BUILDINGS:", "5"], ["FLOORS:", "15"]]),
        ("Lotus Atlantis", "Andheri West", [["FLOORS", "25"]]),
    ]),
    "newwins": dict(panel=["NEW WINS"], cards=[
        ("Ctrl S", "Hyderabad", [["MW:", "42.8"], ["SCOPE:", "MEP"], ["VALUE:", "52 CRS"]]),
        ("BOM 10", "Mumbai", [["MW:", "24 MW"], ["SCOPE:", "HVAC"], ["VALUE:", "40 CRS"]]),
        ("Hinduja Diagnostic Centre", "Mumbai", [["AREA", "88k"], ["SCOPE", "MEP"], ["VALUE:", "25 CRS"]]),
        ("DC", "Navi Mumbai", [["MW:", "80"], ["SCOPE:", "Fire Fighting & Plumbing"], ["VALUE", "31 CRS"]]),
        ("Solitaire MTM 1,2 & 3", "Pune", [["AREA:", "5L"], ["SCOPE:", "Electrical, Basebuild"], ["VALUE", "24 CRS"]]),
        ("SUMITOMO BKC 1", "Mumbai", [["AREA:", "12,00,000"], ["SCOPE:", "Basebuild - HVAC"], ["VALUE", "15 CRS"]]),
    ]),
    "mep1": dict(panel=["MAJOR MEP", "PROJECTS"], cards=[
        ("SIEMENS", "Mumbai", [["AREA", "10L"], ["SCOPE:", "MEP"]]),
        ("Ahuja Towers", "Mumbai", [["AREA:", "11 L"], ["SCOPE:", "MEP"]]),
        ("Solitaire", "Baner & Kharadi", [["AREA:", "5L"], ["SCOPE:", "Electrical"]]),
        ("PURVANKARA", "Navi Mumbai", [["AREA:", "3L"], ["SCOPE:", "Electrical"]]),
        ("MICROMAX", "Noida", [["AREA:", "60k"], ["SCOPE:", "MEP"]]),
        ("PHILIPS", "PUNE", [["AREA:", "2L"], ["SCOPE:", "MEP"]]),
    ]),
    "mep2": dict(panel=["MAJOR MEP", "PROJECTS"], cards=[
        ("Hinduja Diagnostic Centre", "Mumbai", [["AREA", "88k"], ["SCOPE:", "MEP"]]),
        ("Sumitomo 1 & 2nd floor", "Mumbai", [["AREA:", "2,00,000"], ["SCOPE:", "MEP Design & Build"]]),
        ("Foxconn", "Bangalore", [["AREA:", "8,00,000"], ["SCOPE:", "MEP"]]),
        ("Ctrl S", "Mumbai DC 8-9", [["MW", "10"], ["SCOPE:", "MEP GC"]]),
        ("L&T Seawoods", "Navi Mumbai", [["AREA:", "1L"], ["SCOPE:", "MEP"]]),
        ("TVS", "Hossur", [["AREA:", "65,000"], ["SCOPE:", "MEP"]]),
        ("Hyatt Regency", "Pune", [["AREA:", "5,90,000"], ["SCOPE:", "MEP"]]),
        ("SP. Jain", "Mumbai", [["AREA:", "2,00,000"], ["SCOPE:", "MEP"]]),
    ]),
}

# ---- C (plain photos with centred captions)
Cs = {
    "hosp1": dict(title=[[("MAJOR", B, 0), (" HOSPITALITY PROJECTS", R, 0)]], cards=[
        ("Hyatt Regency, Pune", "MEP"), ("Vivanta by Taj, Thane", "MEP"), ("Yogi Midtown Hotel, Mumbai", "HVAC"),
        ("Ibis Navi Mumbai", "HVAC"), ("Double Tree by Hilton Delhi", "HVAC"), ("Click Hotels by Suba Mumbai", "HVAC")]),
    "hosp2": dict(title=[[("MAJOR ", R, 0), ("HOSPITALITY", B, 0), (" PROJECTS", R, 0)]], cards=[
        ("Welcome by ITC Delhi", "MEP"), ("Vivanta by Taj, Miramar", "HVAC"), ("SOHO House Mumbai", "HVAC"),
        ("Sarovar Bodhgaya", "MEP"), ("Hyatt Regency, Delhi", "MEP"), ("Lemon Tree Hotels Gurgoan", "HVAC")]),
    "hosp3": dict(title=[[("MAJOR ", R, 0), ("HOSPITALITY", B, 0), (" PROJECTS", R, 0)]], cards=[
        ("EFFOTEL Navi Mumbai", "HVAC"), ("bloom Hotel Bengaluru", "HVAC"), ("Tropicana Resort & Spa Alibaug", "HVAC"),
        ("Sea N Rock Hotel", "NVRV"), ("Radisson, Alibaug", "HVAC"), ("Royal Orchid, Navi Mumbai", "HVAC")]),
    "hosp4": dict(title=[[("RESTAURANTS", B, 0), (" PROJECTS", R, 0)]], cards=[
        ("Nara Thai Restaurant", "Mumbai", "HVAC"), ("Hakkasan", "Mumbai", "HVAC"), ("GBC", "Pune", "VRV"),
        ("Yauatcha", "Mumbai", "MEP"), ("Gustoso", "Mumbai", "VRV MEP"), ("Bastian", "Lucknow", "MEP")]),
    "vrv": dict(title=[[("MAJOR PROJECTS : ", B, 0), ("VRV", B, 1)]], cards=[
        ("World Trade Center - Pune", "2000", "Commercial"), ("Ahuja - Mumbai", "1800", "Residential"),
        ("Principal Global - Pune", "1600", "Commercial"), ("Crisil - Mumbai", "1200", "Commercial"),
        ("UBS - Pune", "1100", "Commercial"), ("WeWork Futura - Pune", "1000", "Commercial"),
        ("Poonawalla Finance - Pune", "1000", "Commercial"), ("TIAA - Pune", "900", "Commercial"),
        ("Firmenich - Mumbai", "800", "Commercial"), ("Johnson & Johnson - Mumbai", "600", "Commercial"),
        ("Mastercard - Ahmedabad", "600", "Commercial"), ("WeWork Chromium - Mumbai", "450", "Commercial")]),
}

# ---- how the slides appear in the picker: section -> sub-sections (the folders of the BIRA "PROJECT SLIDE" folder) -> slides
SECTIONS = [
    ("Projects — Segment wise", [
        ("BFSI", [("bfsi1", "Major BFSI Projects"), ("bfsi2", "Major BFSI Projects — Across India (1)"), ("bfsi3", "Major BFSI Projects — Across India (2)")]),
        ("CRE", [("cre1", "Major CRE Projects (1)"), ("cre2", "Major CRE Projects (2)")]),
        ("DC", [("dcnew", "New DC Projects"), ("dcmajor", "Major DC Projects")]),
        ("Educational", [("edu", "Major Projects — Education Institutes")]),
        ("Hospitality", [("hosp1", "Major Hospitality Projects (1)"), ("hosp2", "Major Hospitality Projects (2)"), ("hosp3", "Major Hospitality Projects (3)"), ("hosp4", "Restaurants Projects")]),
        ("Industrial Manufacturing", [("ind", "Major Projects — Industrial + Warehousing"), ("mfg", "Project Gallery — Manufacturing")]),
        ("Residential", [("res1", "Major Projects — Private Luxury Residential"), ("res2", "High Rise")]),
    ]),
    ("Projects — Location based", [
        ("South", [("south1", "Major South Projects — Tamil Nadu (1)"), ("south2", "Major BFSI South Projects — Tamil Nadu"), ("south3", "Major South Projects — Tamil Nadu (2)"),
                   ("south4", "Major South Projects — Hyderabad"), ("south5", "Major South Projects — Bangalore")]),
        ("Pune", [("pune1", "Major Projects in Pune (1)"), ("pune3b", "Major Projects in Pune (2)"), ("pune3", "Major Projects in Pune (3)")]),
    ]),
    ("Projects — Scope", [
        ("MEP", [("mep1", "Major MEP Projects (1)"), ("mep2", "Major MEP Projects (2)")]),
        ("VRV", [("vrv", "Major Projects — VRV")]),
    ]),
    ("New Wins", [
        (None, [("newwins", "New Wins")]),
    ]),
]
