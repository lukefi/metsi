from lukefi.metsi.domain.utils.enums import SiteTypeKey

def site_type_to_key(value: int) -> SiteTypeKey:
    """  converts site type of stand into a key for thinning limist lookup table

    site_type variable explanations:
    (1) very rich sites (OMaT in South Finland)
    (2) rich sites (OMT in South Finland)
    (3) damp sites (MT in South Finland)
    (4) sub-dry sites (VT in South Finland)
    (5) dry sites (CT in South Finland)
    (6) barren sites (ClT in South Finland)
    (7) rocky or sandy areas
    (8) open mountains

    """
    if value in (1,2):
        return SiteTypeKey.OMT
    if value in (3,):
        return SiteTypeKey.MT
    if value in (4,):
        return SiteTypeKey.VT
    if value in (5, 6, 7, 8):
        return SiteTypeKey.CT
    if value < 1 or value > 8:
        return SiteTypeKey.MT
    raise UserWarning(f'Unable to spesify site type value {value} as key for the thinning limits lookup table')
