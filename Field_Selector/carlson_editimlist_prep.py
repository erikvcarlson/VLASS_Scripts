def carlson_editimlist_prep(msfile, imagesize, phase_center, matchregex=['^0', '^1', '^2']):
#must be run with VLASS version of CASA to allow for casa_tools to work properly
#carlson_editimlist_prep('VLASS2.1.sb38561374.eb38565040.59070.62333981482.ms/',500,'J2000 08:07:57.5 +04.32.34.6', matchregex=['^0', '^1', '^2'])       
    from pipeline.infrastructure import casa_tools
    import numpy
    
    buffer_arcsec = 1000 #Primary beam in arcseconds at 20%
    dist_arcsec = imagesize + buffer_arcsec
    dist_arcsec = str(dist_arcsec) + 'arcsec'
    distance = dist_arcsec
    
    # Created STM 2016-May-16 use center direction measure
    # Returns list of fields from msfile within a rectangular box of size distance

    qa = casa_tools.quanta
    me = casa_tools.measures
    tb = casa_tools.table

    #msfile = self.vislist[0]

    fieldlist = []

    phase_center = phase_center.split()
    print(phase_center)
    center_dir = me.direction(phase_center[0], phase_center[1], phase_center[2])
    center_ra = center_dir['m0']['value']
    center_dec = center_dir['m1']['value']

    try:
        qdist = qa.toangle(distance)
        qrad = qa.convert(qdist, 'rad')
        maxrad = qrad['value']
    except:
        print('ERROR: cannot parse distance {}'.format(distance))
        return

    try:
        tb.open(msfile + '/FIELD')
    except:
        print('ERROR: could not open {}/FIELD'.format(msfile))
        return
    field_dirs = tb.getcol('PHASE_DIR')
    field_names = tb.getcol('NAME')
    tb.close()

    (nd, ni, nf) = field_dirs.shape
    print('Found {} fields'.format(nf))

    # compile field dictionaries
    ddirs = {}
    flookup = {}
    for i in range(nf):
        fra = field_dirs[0, 0, i]
        fdd = field_dirs[1, 0, i]
        rapos = qa.quantity(fra, 'rad')
        decpos = qa.quantity(fdd, 'rad')
        ral = qa.angle(rapos, form=["tim"], prec=9)
        decl = qa.angle(decpos, prec=10)
        fdir = me.direction('J2000', ral[0], decl[0])
        ddirs[i] = {}
        ddirs[i]['ra'] = fra
        ddirs[i]['dec'] = fdd
        ddirs[i]['dir'] = fdir
        fn = field_names[i]
        ddirs[i]['name'] = fn
        if fn in flookup:
            flookup[fn].append(i)
        else:
            flookup[fn] = [i]
    print('Cataloged {} fields'.format(nf))

    # Construct offset separations in ra,dec
    print('Looking for fields with maximum separation {}'.format(distance))
    nreject = 0
    skipmatch = matchregex == '' or matchregex == []
    for i in range(nf):
        dd = ddirs[i]['dir']
        dd_ra = dd['m0']['value']
        dd_dec = dd['m1']['value']
        sep_ra = abs(dd_ra - center_ra)
        if sep_ra > numpy.pi:
            sep_ra = 2.0 * numpy.pi - sep_ra
        # change the following to use dd_dec 2017-02-06
        sep_ra_sky = sep_ra * numpy.cos(dd_dec)

        sep_dec = abs(dd_dec - center_dec)

        ddirs[i]['offset_ra'] = sep_ra_sky
        ddirs[i]['offset_ra'] = sep_dec

        if sep_ra_sky <= maxrad and sep_dec <= maxrad:
            if skipmatch:
                fieldlist.append(i)
            else:
                # test regex against name
                foundmatch = False
                fn = ddirs[i]['name']
                for rx in matchregex:
                    mat = re.findall(rx, fn)
                    if len(mat) > 0:
                        foundmatch = True
                if foundmatch:
                    fieldlist.append(i)
                else:
                    nreject += 1

    print('Found {} fields within {}'.format(len(fieldlist), distance))
    if not skipmatch:
        print('Rejected {} distance matches for regex'.format(nreject))

    fieldlist = [str(i) for i in fieldlist]
    str1 = ','.join(fieldlist)
    fieldlist = str1 

    return fieldlist
