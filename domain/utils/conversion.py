from domain.utils.enums import SiteTypeKey

def site_type_to_key(value: int) -> str:
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
    elif value in (3,):
        return SiteTypeKey.MT
    elif value in (4,):
        return SiteTypeKey.VT
    elif value in (5, 6, 7, 8):
        return SiteTypeKey.CT
    elif value < 1 or value > 8:
        return SiteTypeKey.MT
    else:
        raise UserWarning('Unable to spesify site type value {} as key for the thinning limits lookup table'.format(value))
