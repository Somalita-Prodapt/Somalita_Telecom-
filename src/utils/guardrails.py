import re

MAX_QUERY_LENGTH = 1000
BLOCKED_PATTERNS = [
    r"<script",
    r"javascript:",
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"disregard\s+(all\s+)?(rules|instructions)",
    r"<\s*iframe",
]

TELECOM_DOMAIN_PATTERNS = [
    # Network performance & KPIs
    r"\blatenc(y|ies)\b",
    r"\bthroughput\b",
    r"\bpacket\s*loss\b",
    r"\bpacket[s]?\b",
    r"\bjitter\b",
    r"\bbandwidth\b",
    r"\bping\b",
    r"\brtt\b",
    r"\bdelays?\b",
    r"\bslow\s+response\b",
    r"\bcongestion\b",
    r"\boverload(ed)?\b",
    r"\bcapacity\b",
    r"\btraffic\b",
    r"\bavailability\b",
    r"\buptime\b",
    r"\bdowntime\b",
    r"\bmttr\b",
    r"\bsla\b",
    r"\bkpi[s]?\b",
    r"\bqos\b",
    r"\bqoe\b",
    r"\bcall\s*drops?\b",
    r"\bdropped\s*calls?\b",
    r"\bdrop\s*rate\b",

    # Cellular, Radio & RF
    r"\bcell[s_]?\b",
    r"\btower[s]?\b",
    r"\bsite[s]?\b",
    r"\bsector[s]?\b",
    r"\bantenna[s]?\b",
    r"\bbase\s*stations?\b",
    r"\bgnodeb[s]?\b",
    r"\benodeb[s]?\b",
    r"\bnodeb[s]?\b",
    r"\bran\b",
    r"\boran\b",
    r"\bvran\b",
    r"\bbts\b",
    r"\bbsc\b",
    r"\brnc\b",
    r"\bcoverage\b",
    r"\bsignal[s]?\b",
    r"\brsrp\b",
    r"\brsrq\b",
    r"\bsinr\b",
    r"\brssi\b",
    r"\bcqi\b",
    r"\bmcs\b",
    r"\binterference\b",
    r"\bfading\b",
    r"\battenuation\b",
    r"\brf\b",
    r"\bspectrum\b",
    r"\bfrequenc(y|ies)\b",
    r"\b5g\b",
    r"\b4g\b",
    r"\b3g\b",
    r"\b2g\b",
    r"\blte\b",
    r"\bnr\b",
    r"\bc-band\b",
    r"\bmmwave\b",
    r"\bsub-6\b",
    r"\bcellular\b",
    r"\bmobile\b",
    r"\bbroadband\b",
    r"\bwifi\b",
    r"\bethernet\b",
    r"\bmodem[s]?\b",
    r"\binternet\b",

    # Mobility & Sessions
    r"\bhandover[s]?\b",
    r"\bhandoff[s]?\b",
    r"\broaming\b",
    r"\bmobility\b",
    r"\bconnect(ion|ions|ivity)?\b",
    r"\bdisconnect(ion|ions|ed)?\b",
    r"\battach(ment)?\b",
    r"\bdetach\b",
    r"\bbearer[s]?\b",
    r"\bsession[s]?\b",
    r"\bpaging\b",

    # Faults, Alarms & Operations
    r"\balarm[s]?\b",
    r"\bfault[s]?\b",
    r"\boutage[s]?\b",
    r"\bdegrad(ed|ation|ing)\b",
    r"\b(service|network|link|hardware|system)\s*fail(ure|ures)?\b",
    r"\b(network|cell|site|link|tower|server)\s*down\b",
    r"\broot\s*cause\b",
    r"\bcorrective\s*action[s]?\b",
    r"\btroubleshoot(ing)?\b",
    r"\bdiagnos(e|is|tic|tics)\b",
    r"\bnetops\b",
    r"\bnoc\b",
    r"\btelecom(munications)?\b",
    r"\bcarrier[s]?\b",
    r"\boperator[s]?\b",
    r"\bsubscriber[s]?\b",
    r"\btelemetry\b",
    r"\bincident[s]?\b",
    r"\bnetops[-\d]*\b",

    # Core & Transport Infrastructure
    r"\bnetwork[s]?\b",
    r"\bbackhaul\b",
    r"\bfronthaul\b",
    r"\bmidhaul\b",
    r"\bfiber\b",
    r"\bmicrowave\b",
    r"\brouter[s]?\b",
    r"\bswitch(es)?\b",
    r"\brouting\b",
    r"\bgateway[s]?\b",
    r"\bfirewall[s]?\b",
    r"\bvlan[s]?\b",
    r"\bsubnet[s]?\b",
    r"\bip\b",
    r"\bipv4\b",
    r"\bipv6\b",
    r"\bdns\b",
    r"\bbgp\b",
    r"\bospf\b",
    r"\bmpls\b",
    r"\bupf\b",
    r"\bamf\b",
    r"\bsmf\b",
    r"\bmme\b",
    r"\bsgw\b",
    r"\bpgw\b",
    r"\budm\b",
    r"\bhss\b",
    r"\blink[s]?\b",
    r"\btrunk[s]?\b",
    r"\binterface[s]?\b",
]

TELECOM_DOMAIN_REGEX = re.compile(r"|".join(TELECOM_DOMAIN_PATTERNS), re.IGNORECASE)


def is_telecom_domain_query(query: str) -> bool:
    """Return True if the query contains telecom or network operational vocabulary."""
    return bool(TELECOM_DOMAIN_REGEX.search(query))


def validate_query(query: str, check_domain: bool = True) -> str:
    """
    Validate query for type, length, injection safety, and telecom domain relevance.
    Raises ValueError on validation failure.
    """
    if not isinstance(query, str):
        raise ValueError("query must be a string")
    q = query.strip()
    if not q:
        raise ValueError("query cannot be empty")
    if len(q) > MAX_QUERY_LENGTH:
        raise ValueError("query is too long")
    low = q.lower()
    if any(re.search(p, low) for p in BLOCKED_PATTERNS):
        raise ValueError("query failed input validation")
    if check_domain and not is_telecom_domain_query(low):
        raise ValueError(
            "Query appears unrelated to telecom/network operations. "
            "Please describe a network symptom, KPI, or incident."
        )
    return q
