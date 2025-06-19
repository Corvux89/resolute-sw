def get_csp(nonce):
    csp = {
        "default-src": [
            "'self'",
            f"nonce-{nonce}",
            "https://docs.google.com",
            "https://code.jquery.com/",
            "https://cdn.jsdelivr.net/",
            "https://www.googletagmanager.com/",
            "https://analytics.google.com/",
            "https://www.google-analytics.com/",
            "https://use.fontawesome.com",
            "https://otfbm.io/",
            "https://discordapp.com/api",
        ],
        "script-src": [
            "'self'",
            f"nonce-{nonce}",
            "https://cdn.jsdelivr.net/",
            "https://www.googletagmanager.com/",
            "https://ajax.googleapis.com",
            "https://cdn.datatables.net/",
            "https://cdnjs.cloudflare.com/ajax/",
        ],
        "img-src": ["*", "'self'", "data:"],
        "style-src": [
            "'self'",
            f"nonce-{nonce}",
            "https://use.fontawesome.com",
            "https://cdn.jsdelivr.net/",
            "https://cdn.datatables.net/",
            "https://fonts.googleapis.com/",
            "https://maxcdn.bootstrapcdn.com/",
        ],
        "font-src": [
            "'self'",
            f"nonce-{nonce}",
            "https://use.fontawesome.com",
            "https://fonts.gstatic.com/",
            "https://maxcdn.bootstrapcdn.com/",
        ],
    }

    out_csp = "; ".join([f"{key} {value}" for key, value in csp.items()])
    return out_csp
