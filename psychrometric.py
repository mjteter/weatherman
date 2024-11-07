from math import *


def psych(output_str, input_str_1, input_1, input_str_2, input_2, pressure=29.92):
    """ Function to give properties of wet air.
    output_str: solve for this
    input_str_1: input type
    input_1: input
    input_str_2: input type
    input_2: input
    pressure (default=29.92): pressure of air (in Hg)

    Valid input/outpu strings:
    db/DB = dry bulb temperature (deg F)
    wb/WB = wet bulb temperature (deg F)
    dp/DP = dewpoint temperature (deg F)
    rh/RH = relative humidity (0-100 percentage)
    hr/HR = humidity ratio (lb/lb)
    sv/SV = specific volume (ft^3/lb dry air)
    en/EN = enthalpy (Btu/lb dry air
    """

    dry_bulb = 0
    wet_bulb = 0
    dewpoint = 0
    rel_hum = 0
    hum_rat = 0
    spec_vol = 0
    enthalpy = 0
    pressure *= 0.491154

    if input_str_1 in ('db', 'DB', 'wb', 'WB', 'dp', 'DP', 'rh', 'RH', 'hr', 'HR', 'sv', 'SV', 'en', 'EN') and \
       input_str_2 in ('db', 'DB', 'wb', 'WB', 'dp', 'DP', 'rh', 'RH', 'hr', 'HR', 'sv', 'SV', 'en', 'EN'):

        if input_str_1 in ('db', 'DB'):
            dry_bulb = input_1
        elif input_str_2 in ('db', 'DB'):
            dry_bulb = input_2

        if input_str_1 in ('wb', 'WB'):
            wet_bulb = input_1
        elif input_str_2 in ('wb', 'WB'):
            wet_bulb = input_2

        if input_str_1 in ('dp', 'DP'):
            dewpoint = input_1
        elif input_str_2 in ('dp', 'DP'):
            dewpoint = input_2

        if input_str_1 in ('rh', 'RH'):
            rel_hum = input_1 / 100
        elif input_str_2 in ('rh', 'RH'):
            rel_hum = input_2 / 100

        if input_str_1 in ('hr', 'HR'):
            hum_rat = input_1
        elif input_str_2 in ('hr', 'HR'):
            hum_rat = input_2

        if input_str_1 in ('sv', 'SV'):
            spec_vol = input_1
        elif input_str_2 in ('sv', 'SV'):
            spec_vol = input_2

        if input_str_1 in ('en', 'EN'):
            enthalpy = input_1
        elif input_str_2 in ('en', 'EN'):
            enthalpy = input_2
    else:
        return ValueError('Invalid input types')

    if hum_rat < 0:
        return ValueError('Humidity ratio less than 0')
    if rel_hum < 0 or rel_hum > 1:
        return ValueError('Relative humidity less than 0 or greater than 100')

    ############################################################################################

    if input_str_1 in ('db', 'DB') or input_str_2 in ('db', 'DB'):
        if output_str in ('db', 'DB'):
            return dry_bulb

        db_r = dry_bulb + 459.67

        if input_str_1 in ('wb', 'WB') or input_str_2 in ('wb', 'WB'):
            if output_str in ('wb', 'WB'):
                return wet_bulb

            db_r = dry_bulb + 459.67
            wb_r = wet_bulb + 459.67

            pres_wb_sat = sat_pres(wb_r)

            hr_wb_sat = 0.62198 * pres_wb_sat / (pressure - pres_wb_sat)

            hum_rat = (hr_wb_sat * (1093 - .556 * wet_bulb) - 0.24 * (dry_bulb - wet_bulb)) / \
                      (1093 + .444 * dry_bulb - wet_bulb)
            if output_str in ('hr', 'HR'):
                return hum_rat

            pres_db_sat = sat_pres(db_r)

            hr_db_sat = 0.62198 * pres_db_sat / (pressure - pres_db_sat)

            mu = hum_rat / hr_db_sat

            rel_hum = mu / (1 - (1 - mu) * (pres_db_sat / pressure))
            if rel_hum < 0 or rel_hum > 1:
                return -1  # ValueError('Calculated relative humidity less than 0')
            if output_str in ('rh', 'RH'):
                return rel_hum * 100

            if output_str in ('sv', 'SV'):
                spec_vol = 1545.32 * db_r * (1 + 1.6078 * hum_rat) / (28.9645 * pressure * 144)
                return spec_vol

            if output_str in ('en', 'EN'):
                enthalpy = 0.24 * dry_bulb + hum_rat * (1061 + 0.444 * dry_bulb)
                return enthalpy

            if output_str in ('dp', 'DP'):
                pres_vapor = (pressure * hum_rat) / (0.62198 + hum_rat)

                dewpoint = calc_dewpoint(pres_vapor)
                return dewpoint
            else:
                return ValueError('Unknown output request')
        elif input_str_1 in ('dp', 'DP') or input_str_2 in ('dp', 'DP'):
            if output_str in ('dp', 'DP'):
                return dewpoint

            dp_r = dewpoint + 459.67

            pres_vapor = sat_pres(dp_r)

            hum_rat = 0.62198 * pres_vapor / (pressure - pres_vapor)
            if hum_rat < 0:
                return -1  # ValueError('Calculated humidity ratio below 0')
            if output_str in ('hr', 'HR'):
                return hum_rat

            pres_db_sat = sat_pres(db_r)

            hr_db_sat = 0.62198 * pres_db_sat / (pressure - pres_db_sat)

            mu = hum_rat / hr_db_sat

            rel_hum = mu / (1 - (1 - mu) * (pres_db_sat / pressure))
            if rel_hum < 0 or rel_hum > 1:
                return -1
            if output_str in ('rh', 'RH'):
                return rel_hum * 100

            if output_str in ('sv', 'SV'):
                spec_vol = 1545.32 * db_r * (1 + 1.6078 * hum_rat) / (28.9645 * pressure * 144)
                return spec_vol

            if output_str in ('en', 'EN'):
                enthalpy = 0.24 * dry_bulb + hum_rat * (1061 + 0.444 * dry_bulb)
                return enthalpy

            if output_str in ('wb', 'WB'):
                wet_bulb = calc_wetbulb(dry_bulb, hum_rat, pressure)
                return wet_bulb
            else:
                return ValueError('Unknown output request')
        elif input_str_1 in ('rh', 'RH') or input_str_2 in ('rh', 'RH'):
            if output_str in ('rh', 'RH'):
                return rel_hum * 100

            pres_db_sat = sat_pres(db_r)

            pres_vapor = pres_db_sat * rel_hum

            hum_rat = 0.62198 * pres_vapor / (pressure - pres_vapor)
            if hum_rat < 0:
                return -1
            if output_str in ('hr', 'HR'):
                return hum_rat

            # hr_db_sat = 0.62198 * pres_db_sat / (pressure - pres_db_sat)

            # mu = hum_rat / hr_db_sat

            if output_str in ('sv', 'SV'):
                spec_vol = 1545.32 * db_r * (1 + 1.6078 * hum_rat) / (28.9645 * pressure * 144)
                return spec_vol

            if output_str in ('en', 'EN'):
                enthalpy = 0.24 * dry_bulb + hum_rat * (1061 + 0.444 * dry_bulb)
                return enthalpy

            if output_str in ('dp', 'DP'):
                dewpoint = calc_dewpoint(pres_vapor)
                return dewpoint

            if output_str in ('wb', 'WB'):
                wet_bulb = calc_wetbulb(dry_bulb, hum_rat, pressure)
                return wet_bulb
            else:
                return ValueError('Unknown output request')
        elif input_str_1 in ('hr', 'HR') or input_str_2 in ('hr', 'HR'):
            if output_str in ('hr', 'HR'):
                return hum_rat

            pres_db_sat = sat_pres(db_r)

            pres_vapor = hum_rat * pressure / (hum_rat + 0.62198)

            rel_hum = pres_vapor / pres_db_sat
            if rel_hum < 0 or rel_hum > 1:
                return -1
            if output_str in ('rh', 'RH'):
                return rel_hum * 100

            # hr_db_sat = 0.62198 * pres_db_sat / (pressure - pres_db_sat)

            # mu = hum_rat / hr_db_sat

            if output_str in ('sv', 'SV'):
                spec_vol = 1545.32 * db_r * (1 + 1.6078 * hum_rat) / (28.9645 * pressure * 144)
                return spec_vol

            if output_str in ('en', 'EN'):
                enthalpy = 0.24 * dry_bulb + hum_rat * (1061 + 0.444 * dry_bulb)
                return enthalpy

            if output_str in ('dp', 'DP'):
                dewpoint = calc_dewpoint(pres_vapor)
                return dewpoint

            if output_str in ('wb', 'WB'):
                wet_bulb = calc_wetbulb(dry_bulb, hum_rat, pressure)
                return wet_bulb
            else:
                return ValueError('Unknown output request')
        elif input_str_1 in ('sv', 'SV') or input_str_2 in ('sv', 'SV'):
            if output_str in ('sv', 'SV'):
                return spec_vol

            # pres_db_sat = sat_pres(db_r)

            hum_rat = (spec_vol * 28.9645 * (pressure * 144) / (1545.32 * db_r) - 1) / 1.6078
            if hum_rat < 0:
                return -1
            if output_str in ('hr', 'HR'):
                return hum_rat

            pres_vapor = hum_rat * pressure / (hum_rat + 0.62198)

            rel_hum = pres_vapor / pressure
            if rel_hum < 0 or rel_hum > 1:
                return -1
            if output_str in ('rh', 'RH'):
                return rel_hum * 100

            if output_str in ('en', 'EN'):
                enthalpy = 0.24 * dry_bulb + hum_rat * (1061 + 0.444 * dry_bulb)
                return enthalpy

            if output_str in ('dp', 'DP'):
                dewpoint = calc_dewpoint(pres_vapor)
                return dewpoint

            if output_str in ('wb', 'WB'):
                wet_bulb = calc_wetbulb(dry_bulb, hum_rat, pressure)
                return wet_bulb
            else:
                return ValueError('Unknown output request')
        elif input_str_1 in ('en', 'EN') or input_str_2 in ('en', 'EN'):
            if output_str in ('en', 'EN'):
                return enthalpy

            pres_db_sat = sat_pres(dry_bulb)

            hum_rat = (enthalpy - 0.24 * dry_bulb) / (1061 + 0.444 * dry_bulb)
            if hum_rat < 0:
                return -1
            if output_str in ('hr', 'HR'):
                return hum_rat

            pres_vapor = hum_rat * pressure / (hum_rat + 0.62198)

            rel_hum = pres_vapor / pres_db_sat
            if rel_hum < 0 or rel_hum > 1:
                return -1
            if output_str in ('rh', 'RH'):
                return rel_hum * 100

            # hr_db_sat = 0.62198 * pres_db_sat / (pressure - pres_db_sat)

            # mu = hum_rat / hr_db_sat

            if output_str in ('sv', 'SV'):
                spec_vol = 1545.32 * db_r * (1 + 1.6078 * hum_rat) / (28.9645 * pressure * 144)
                return spec_vol

            if output_str in ('dp', 'DP'):
                dewpoint = calc_dewpoint(pres_vapor)
                return dewpoint

            if output_str in ('wb', 'WB'):
                wet_bulb = calc_wetbulb(dry_bulb, hum_rat, pressure)
                return wet_bulb
            else:
                return ValueError('Unknown output request')
    elif input_str_1 in ('wb', 'WB') or input_str_2 in ('wb', 'WB'):
        if output_str in ('wb', 'WB'):
            return wet_bulb

        wb_r = wet_bulb + 459.67

        if input_str_1 in ('dp', 'DP') or input_str_2 in ('dp', 'DP'):
            if output_str in ('dp', 'DP'):
                return dewpoint

            dp_r = dewpoint + 459.67

            pres_vapor = sat_pres(dp_r)

            hum_rat = 0.62198 * pres_vapor / (pressure - pres_vapor)
            if hum_rat < 0:
                return -1
            if output_str in ('hr', 'HR'):
                return hum_rat

            pres_wb_sat = sat_pres(wb_r)

            hr_wb_sat = 0.62198 * pres_wb_sat / (pressure - pres_wb_sat)

            dry_bulb = ((1093 - 0.556 * wet_bulb) * hr_wb_sat + 0.24 * wet_bulb - (1093 - wet_bulb) * hum_rat) / \
                       (0.444 * hum_rat + 0.24)
            if output_str in ('db', 'DB'):
                return dry_bulb

            db_r = dry_bulb + 459.67

            pres_db_sat = sat_pres(dry_bulb)

            hr_db_sat = 0.62198 * pres_db_sat / (pressure - pres_db_sat)
            mu = hum_rat / hr_db_sat

            rel_hum = mu / (1 - (1 - mu) * (pres_db_sat / pressure))
            if rel_hum < 0 or rel_hum > 1:
                return -1
            if output_str in ('rh', 'RH'):
                return rel_hum

            if output_str in ('sv', 'SV'):
                spec_vol = 1545.32 * db_r * (1 + 1.6078 * hum_rat) / (28.9645 * pressure * 144)
                return spec_vol

            if output_str in ('en', 'EN'):
                enthalpy = 0.24 * dry_bulb + hum_rat * (1061 + 0.444 * dry_bulb)
                return enthalpy
            else:
                return ValueError('Unknown output request')
        elif input_str_1 in ('rh', 'RH') or input_str_2 in ('rh', 'RH'):
            if output_str in ('rh', 'RH'):
                return rel_hum * 100
        elif input_str_1 in ('hr', 'HR') or input_str_2 in ('hr', 'HR'):
            if output_str in ('hr', 'HR'):
                return hum_rat
        elif input_str_1 in ('sv', 'SV') or input_str_2 in ('sv', 'SV'):
            if output_str in ('sv', 'SV'):
                return spec_vol
        elif input_str_1 in ('en', 'EN') or input_str_2 in ('en', 'EN'):
            if output_str in ('en', 'EN'):
                return enthalpy
            return -1  # no enthalpy, wet bulb and enthalpy are too closely related to avoid problems
    elif input_str_1 in ('dp', 'DP') or input_str_2 in ('dp', 'DP'):
        if output_str in ('dp', 'DP'):
            return dewpoint

        dp_r = dewpoint + 459.67

        if input_str_1 in ('rh', 'RH') or input_str_2 in ('rh', 'RH'):
            if output_str in ('rh', 'RH'):
                return rel_hum * 100
        elif input_str_1 in ('sv', 'SV') or input_str_2 in ('sv', 'SV'):
            if output_str in ('sv', 'SV'):
                return spec_vol
        elif input_str_1 in ('en', 'EN') or input_str_2 in ('en', 'EN'):
            if output_str in ('en', 'EN'):
                return enthalpy
        elif input_str_1 in ('hr', 'HR') or input_str_2 in ('hr', 'HR'):
            if output_str in ('hr', 'HR'):
                return hum_rat
            return -1  # no humidity ratio - it is the dew point more or less
    elif input_str_1 in ('hr', 'HR') or input_str_2 in ('hr', 'HR'):
        if output_str in ('hr', 'HR'):
            return hum_rat

        if input_str_1 in ('rh', 'RH') or input_str_2 in ('rh', 'RH'):
            if output_str in ('rh', 'RH'):
                return rel_hum * 100
        elif input_str_1 in ('sv', 'SV') or input_str_2 in ('sv', 'SV'):
            if output_str in ('sv', 'SV'):
                return spec_vol
        elif input_str_1 in ('en', 'EN') or input_str_2 in ('en', 'EN'):
            if output_str in ('en', 'EN'):
                return enthalpy
    elif input_str_1 in ('rh', 'RH') or input_str_2 in ('rh', 'RH'):
        if output_str in ('rh', 'RH'):
            return rel_hum * 100

        if input_str_1 in ('sv', 'SV') or input_str_2 in ('sv', 'SV'):
            if output_str in ('sv', 'SV'):
                return spec_vol
        elif input_str_1 in ('en', 'EN') or input_str_2 in ('en', 'EN'):
            if output_str in ('en', 'EN'):
                return enthalpy
    elif input_str_1 in ('sv', 'SV') or input_str_2 in ('sv', 'SV'):
        if output_str in ('sv', 'SV'):
            return spec_vol

        if input_str_1 in ('en', 'EN') or input_str_2 in ('en', 'EN'):
            if output_str in ('en', 'EN'):
                return enthalpy


def calc_wetbulb(dry_bulb, hum_rat, pressure):
    wet_bulb = dry_bulb
    ii = 0

    while ii < 500:
        ii += 1

        wb_r = wet_bulb + 459.67

        pres_wb_sat = sat_pres(wb_r)

        hr_wb_sat = 0.62198 * pres_wb_sat / (pressure - pres_wb_sat)

        hr_temp = (hr_wb_sat * (1093 - 0.556 * wet_bulb) - 0.24 * (dry_bulb - wet_bulb)) / \
                  (1093 + 0.444 * dry_bulb - wet_bulb)

        if abs(hr_temp / hum_rat - 1) < 0.000001:
            break

        wet_bulb *= (hum_rat / hr_temp) ** 0.01
    return wet_bulb


def calc_dewpoint(pres_vapor):
    dewpoint = 100.45 + 33.193 * log(pres_vapor) + 2.319 * log(pres_vapor) ** 2 + \
               0.17074 * log(pres_vapor) ** 3 + 1.2063 * pres_vapor ** 0.1984
    if dewpoint < 32:
        dewpoint = 90.12 + 26.142 * log(pres_vapor) + 0.8927 * log(pres_vapor) ** 2
    return dewpoint


def calc_heat_index(dry_bulb, rel_hum):
    hi = ((-42.379 + 2.04901523 * dry_bulb + 10.14333127 * rel_hum - 0.22475541 * dry_bulb * rel_hum -
          0.00683783 * dry_bulb ** 2 - 0.05481717 * rel_hum ** 2) + 0.00122874 * dry_bulb ** 2 * rel_hum +
          0.00085282 * dry_bulb * rel_hum ** 2 - 0.00000199 * dry_bulb ** 2 * rel_hum ** 2)

    return hi


def sat_pres(temp):
    if temp - 459.67 > 32:
        return exp(-10440.397 / temp - 11.29465 - 0.027022355 * temp + 0.00001289036 * temp ** 2 - 2.4780681e-9 *
                   temp ** 3 + 6.5459673 * log(temp))
    else:
        return exp(-10214.165 / temp - 4.8932428 - 0.0053765794 * temp + 0.00000019202377 * temp ** 2 +
                   3.5575832e-10 * temp ** 3 - 9.0344688e-14 * temp ** 4 + 4.1635019 * log(temp))
