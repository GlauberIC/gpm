'''

GPM VALIDATION

'''

import numpy as np
import datetime as dt
import wradlib as wrl

def test(arry):
    print 'Shape: ', arry.shape
    print 'NaN Min: ', np.nanmin(arry)
    print 'NaN Max: ', np.nanmax(arry)
    print 'Min: ', np.min(arry)
    print 'Max: ', np.max(arry)
    print 'Unique: ', np.unique(arry)

def dscat(xdat, ydat):
    # Todo: erstellen ScatterHistogramplot
    import matplotlib.pyplot as plt, numpy as np, numpy.random, scipy
    #data definition
    N = 1000
    #xdat, ydat = np.random.normal(size=N), np.random.normal(size=N)
    #xdat, ydat = np.sin(np.arange(1, N)),np.cos(np.arange(1, N)+10)
    #xdat, ydat = np.array([1,2,3,4,4,4,4,4,4,4]), np.array([1,2,3,4,4,4,4,4,4,4])


    #histogram definition
    xyrange = [[np.nanmin(xdat),np.nanmax(xdat)],[np.nanmin(ydat),np.nanmax(ydat)]] # data range
    bins = [100,100] # number of bins
    thresh = 0.1  #density threshold

    #linear regression
    from scipy import stats
    mask = ~np.isnan(xdat) & ~np.isnan(xdat)
    slope, intercept, r_value, p_value, std_err = stats.linregress(xdat[mask], ydat[mask])
    line = slope * xdat + intercept

    from scipy import stats
    #xdat = xdat.reshape(xdat.shape[0]*xdat.shape[1],)
    #ydat = ydat.reshape(ydat.shape[0]*ydat.shape[1],)

    # histogram the data
    hh, locx, locy = scipy.histogram2d(xdat, ydat, range=xyrange, bins=bins)
    posx = np.digitize(xdat, locx)
    posy = np.digitize(ydat, locy)

    #select points within the histogram
    ind = (posx > 0) & (posx <= bins[0]) & (posy > 0) & (posy <= bins[1])
    hhsub = hh[posx[ind] - 1, posy[ind] - 1] # values of the histogram where the points are
    xdat1 = xdat[ind][hhsub < thresh] # low density points
    ydat1 = ydat[ind][hhsub < thresh]
    hh[hh < thresh] = np.nan # fill the areas with low density by NaNs

    plt.imshow(np.flipud(hh.T),cmap='jet',extent=np.array(xyrange).flatten(), interpolation='none', origin='upper')
    plt.colorbar()
    plt.plot(xdat1, ydat1, '.',color='darkblue')
    plt.plot(xdat, line, 'r', label = 'Korrelation \n' + str(round(r_value, 3))
                                           + r'$\pm$' + str(round(std_err, 3)))
    print xdat, xdat1
    plt.legend(loc='upper left', ncol=1, fancybox=True, shadow=True,
               fontsize='20')
    plt.xlim(xyrange[0])
    plt.ylim(xyrange[1])
    plt.grid()




def rmse(predictions, targets):
    # Berechnung von RMSE
    # Todo: Weitere berechnung mit RMS etc einfugen
    import numpy as np
    # RMS sqrt(1/n SUM/d_i - pi)^2
    return np.sqrt(((predictions - targets) ** 2).mean())

def bias(est,ref):
    # Todo: zum laufen bringen
    import numpy as np
    bias = np.sum(ref-est)/(ref.shape[0]*ref.shape[1])
    return bias

def histo(data1, data2, bino):

    import matplotlib.pyplot as plt
    #Todo: in arbeit
    plt.hist(data1[~np.isnan(data1)], bins=bino, alpha=0.5)
    plt.hist(data2[~np.isnan(data2)], bins=bino, alpha=0.5)
    plt.show()


#Heidke Skill Score
# Lit: J. Tan A Novel Approach to Indetify Source of Errors in IMERG for GPM Ground Validation
#Grundgenauigkeit ist die Trefferate
#                   |  Estimate  |  Reference
#-----------------------------------------------
#Hit H :            |  Yes      |    Yes
#Miss M :           |  No       |    Yes
#F False:           |  Yes      |    No
#C Correctnegative :|  No       |    No


def skill_score(estimate, reference, th=None):
    # SkillScore berechnung
    #contigency tables Lit: Tang et al. 2015
    import numpy as np
    #reshapen von arrays
    try:
        estimate = estimate.reshape(estimate.shape[0]*estimate.shape[1])
        reference = reference.reshape(reference.shape[0]*reference.shape[1])
    except IndexError:
        estimate = estimate
        reference = reference

    if th == None:
        th = 0.1 # GMI 0.1, ka 0.2 ku 0.5 Hou et al 2014
    reference, estimate = np.nan_to_num(reference), np.nan_to_num(estimate)

    #Hit
    H_pos = np.array(np.flatnonzero((estimate > th) & (reference > th)))
    #Miss
    M_pos = np.array(np.flatnonzero((estimate <= th) & (reference > th)))
    #FalseAlarm
    F_pos = np.array(np.flatnonzero((estimate > th) & (reference <= th)))
    #Correctnegative
    C_pos = np.array(np.flatnonzero((estimate <= th) & (reference <= th)))
    #Samplesize
    N = len(estimate)

    H, M, F, C = len(H_pos), len(M_pos), len(F_pos), len(C_pos)

    H, M, F, C, N = float(H), float(M), float(F), float(C), float(N)

    E = 1/N * (((H + M)*(H + F)) +
                       ((C + M) * (C + F)))
    #Entdekungswahrscheinlichkeit
    POD = H/(H + M)
    FAR = F/(H + F)
    BID = (H +F)/(H + M)
    HSS = (H + C - E) / (N - E)
    #Trefferrate
    HR = (H+C)/N
    #Bias RMSE
    #RMSE=sqrt(sum((yobs-yest).^2)/(length(yobs)-1));
    #Ytemp=[ones(11,1) yest'];
    #B=Ytemp\yobs';
    # nach Sungmin 2016
    # TODO: Bias in extra funktion!
    bias = np.nansum(estimate-reference)/H
    rmse = np.sqrt(np.nansum(((estimate-reference)**2)/H))
    result = {'H': H,
              'M': M,
              'F': F,
              'C': C,
              'H_pos': H_pos,
              'M_pos': M_pos,
              'F_pos': F_pos,
              'C_pos': C_pos,
              'N': N,
              'HR': HR,
              'POD': POD,
              'FAR': FAR,
              'BID': BID,
              'HSS': HSS,
              'bias': bias,
              'RMSE': rmse}

    #for key, value in result.items():
    #    print(key + ':', value)

    return result



def plot_score(estimate, reference, scoreval):
    # ein Skill Score Plot
    # Todo: gestaltung verbessern
    import numpy as np
    #reshapen von arrays
    try:
        estimate = estimate.reshape(estimate.shape[0]*estimate.shape[1])
        reference = reference.reshape(reference.shape[0]*reference.shape[1])
    except IndexError:
        estimate = estimate
        reference = reference

    import matplotlib.pyplot as plt

    plt.scatter(estimate[scoreval['H_pos']],reference[scoreval['H_pos']],
                color='blue', label='Hit')
    plt.scatter(estimate[scoreval['M_pos']],reference[scoreval['M_pos']],
                color='orange', label='Miss')
    plt.scatter(estimate[scoreval['F_pos']],reference[scoreval['F_pos']],
                color='red', label='False')
    plt.scatter(estimate[scoreval['C_pos']],reference[scoreval['C_pos']],
                color='green', label='Correct Negative')
    plt.grid()
    plt.legend(loc='upper left')
    plt.figtext(0.005,0.005,' POD: '+ str(np.round(scoreval['POD'],3))+
                ' , ' + ' FAR: ' + str(np.round(scoreval['FAR'],3)) +
                ', '+ 'BID: ' + str(np.round(scoreval['BID'],3)) +
              ', ' + ' HSS: ' + str(np.round(scoreval['HSS'],3)) +
                '-- H: '+ str(scoreval['H']) + ', ' +
                ' M: ' + str(scoreval['M']) + ', ' +
                ' F: '+ str(scoreval['F']) + ', ' +
                ' C: ' + str(scoreval['C']) + ', '
                ' N: ' + str(scoreval['N'])
                ,fontsize=10)
    #plt.pie([RR['H'],RR['M'],RR['F'],RR['C']], labels=['H','M','F','C'],colors=['b','orange','r','g'],autopct='%1.1f%%', explode=[0.1,0.1,0.1,0.1],shadow=True, startangle=90)

    #plt.show()




def zeitschleife(sY,sm,sd,sH,sM,sS, eY,em,ed,eH,eM,eS,steps):
    # Bestimmung eines Vektor mit aufeinande folgenden Zeitstempeln
    import datetime as dt
    import numpy as np
    ztime = []
    def datespan(startDate, endDate, delta=dt.timedelta(days=1)):
        currentDate = startDate
        while currentDate < endDate:
            yield currentDate
            currentDate += delta

    start = dt.datetime(sY, sm, sd, sH, sM,sS)
    ende = dt.datetime(eY, em, ed, eH, eM,eS)
    ztime=[]
    if steps == None:
        stteps = 5

    for timestamp in datespan(start,ende,delta=dt.timedelta(minutes=steps)):
        ztime.append(timestamp.strftime('%Y%m%d%H%M%S'))


        #print timestamp.strftime('%Y%m%d%H%M%S')
        #return timestamp.strftime('%Y%m%d%H%M%S')
    return ztime


#### Idee
#Todo: Korrelation von Radar und Satellit Daten in bestimmten Bereichen
# Z.B. Nur bestimmte Niederschlagsintensiteten!
#RR1_3 = A[mask]
#GR1_3 = B[mask]
#
#Rmin, Rmax = 2, 6#
#
#RR1_3[RR1_3 < Rmin] = np.nan
#GR1_3[GR1_3< Rmax] = np.nan
#
#RR1_3[RR1_3 > Rmin] = np.nan
#GR1_3[GR1_3> Rmax] = np.nan
#
#plt.scatter(RR1_3,GR1_3)
#from pcc import rmse
#plt.title(str(rmse(RR1_3,GR1_3)))
#plt.show()

#ag = gpm_gpm.reshape(gpm_gpm.shape[0]*gpm_gpm.shape[1])
#ar = rrr.reshape(rrr.shape[0]*rrr.shape[1])
def plot_world(ax,lon1, lon2, lat1, lat2):

    from osgeo import osr
    wgs84 = osr.SpatialReference()
    wgs84.ImportFromEPSG(4326)

    filename = wrl.util.get_wradlib_data_file('geo/ne_10m_admin_0_countries.shp')

    dataset, inLayer = wrl.io.open_shape(filename)
    inLayer.SetSpatialFilterRect(lon1, lat1, lon2, lat2)
    borders, keys = wrl.georef.get_shape_coordinates(inLayer, key='name')
    wrl.vis.add_lines(ax, borders, color='black', lw=1, zorder=4)
    ax.autoscale()

def z2r2(z):
    # Nach E. Goudenhoofdt and L. Delobbe 2016
    # DWD Abschlussbericht
    z[np.where(z <=36.)] = ((z[np.where(z<=36.)])/200.)**(1./1.6)

    z[np.where((36.5 < z)& (z < 44.))] = ((z[np.where((36.5 < z)& (z < 44.))])/200.)**(1./1.6)

    z[np.where(z > 44.)] = ((z[np.where(z > 44.)])/77.)**(1./1.9)
    return z

def plot_ocean(ax):
    # Grenzen der Kuesten
    import wradlib
    from osgeo import osr
    import os
    import wradlib as wrl
    import numpy as np

    filename = os.path.join('/automount/db01/python/data/NED/10m/physical/10m_physical/ne_10m_ocean.shp')
    dataset, inLayer = wradlib.io.open_shape(filename)
    inLayer.SetSpatialFilterRect(1, 45, 19, 56.5)
    borders, keys = wradlib.georef.get_shape_coordinates(inLayer)
    proj_gk = osr.SpatialReference()
    proj_gk.ImportFromEPSG(31466)
    proj_ll = osr.SpatialReference()
    proj_ll.ImportFromEPSG(4326)
    gk3 = wradlib.georef.epsg_to_osr(31467)
    proj_stereo = wrl.georef.create_osr("dwd-radolan")
    proj_wgs = osr.SpatialReference()
    proj_wgs.ImportFromEPSG(4326)
    print borders.shape

    for j in range(borders.shape[0]):
        bu = np.array(borders[j].shape)

        a = np.array(bu.shape)

        if a==1:
            for i in range(0,borders[j].shape[0],1):
                bordx, bordy = wrl.georef.reproject(borders[j][i][:,0], borders[j][i][:,1], projection_source=proj_wgs, projection_target=proj_stereo)
                bord_xy = np.vstack((bordx.ravel(), bordy.ravel())).transpose()
                wradlib.vis.add_lines(ax, bord_xy, color='black', lw=2, zorder=3)
        if a==2:    #richtig
            bordx, bordy = wrl.georef.reproject(borders[j][:,0], borders[j][:,1], projection_source=proj_wgs, projection_target=proj_stereo)
            bord_xy = np.vstack((bordx.ravel(), bordy.ravel())).transpose()
            wradlib.vis.add_lines(ax, bord_xy, color='black', lw=2, zorder=3)

        bord_xy = np.vstack((bordx.ravel(), bordy.ravel())).transpose()

        wradlib.vis.add_lines(ax, bord_xy, color='black', lw=2, zorder=3)
    ax.autoscale()

def plot_borders(ax):
    # Landesgrenzen Deutschlands
    from osgeo import osr
    import wradlib as wrl
    import wradlib
    import numpy as np
    wgs84 = osr.SpatialReference()
    wgs84.ImportFromEPSG(4326)
    india = osr.SpatialReference()
    # asia south albers equal area conic
    india.ImportFromEPSG(102028)

    proj_gk = osr.SpatialReference()
    proj_gk.ImportFromEPSG(31466)
    proj_ll = osr.SpatialReference()
    proj_ll.ImportFromEPSG(4326)
    gk3 = wradlib.georef.epsg_to_osr(31467)
    proj_stereo = wrl.georef.create_osr("dwd-radolan")
    proj_wgs = osr.SpatialReference()
    proj_wgs.ImportFromEPSG(4326)

    # country list
    countries = ['Germany']#,'France','Denmark', 'Netherlands', 'Poland']
    # open the input data source and get the layer
    filename = wradlib.util.get_wradlib_data_file('/automount/db01/python/data/NED/10m/cultural/10m_cultural/10m_cultural/ne_10m_admin_0_countries.shp')
    dataset, inLayer = wradlib.io.open_shape(filename)
    # iterate over countries, filter accordingly, get coordinates and plot
    for item in countries:
        #print item
        # SQL-like selection syntax
        fattr = "(name='"+item+"')"
        inLayer.SetAttributeFilter(fattr)
        # get borders and names
        borders, keys = wradlib.georef.get_shape_coordinates(inLayer, key='name')

        for j in range(borders.shape[0]):
            bu = np.array(borders[j].shape)
            a = np.array(bu.shape)

            if a==1:
                for i in range(0,borders[j].shape[0],1):
                    bordx, bordy = wrl.georef.reproject(borders[j][i][:,0], borders[j][i][:,1], projection_source=proj_wgs, projection_target=proj_stereo)
                    bord_xy = np.vstack((bordx.ravel(), bordy.ravel())).transpose()

                    wradlib.vis.add_lines(ax, bord_xy, color='black', lw=2, zorder=3)
            if a==2:    #richtig
                bordx, bordy = wrl.georef.reproject(borders[j][:,0], borders[j][:,1], projection_source=proj_wgs, projection_target=proj_stereo)
                bord_xy = np.vstack((bordx.ravel(), bordy.ravel())).transpose()

                wradlib.vis.add_lines(ax, bord_xy, color='black', lw=2, zorder=3)

            bord_xy = np.vstack((bordx.ravel(), bordy.ravel())).transpose()

            wradlib.vis.add_lines(ax, bord_xy, color='black', lw=2, zorder=3)
    ax.autoscale()
'''
def plot_dem(ax):
    filename = wrl.util.get_wradlib_data_file('geo/bangladesh.tif')
    # pixel_spacing is in output units (lonlat)
    rastercoords, rastervalues = wrl.io.read_raster_data(filename,
                                                         spacing=0.005)
    # specify kwargs for plotting, using terrain colormap and LogNorm
    dem = ax.pcolormesh(rastercoords[..., 0], rastercoords[..., 1],
                        rastervalues, cmap=pl.cm.terrain, norm=LogNorm(),
                        vmin=1, vmax=3000)
    # make some space on the right for colorbar axis
    div1 = make_axes_locatable(ax)
    cax1 = div1.append_axes("right", size="5%", pad=0.1)
    # add colorbar and title
    # we use LogLocator for colorbar
    cb = pl.gcf().colorbar(dem, cax=cax1,
                           ticks=ticker.LogLocator(subs=range(10)))
    cb.set_label('terrain height [m]')
'''
def boxpol_pos():
    # Koordinaten des Bonner Radar
    pos_boxpol = {'lat_ppi' : 50.730519999999999, 'lon_ppi' : 7.071663
    ,'gky_ppi' : -4235.233235191105, 'gkx_ppi' : -216.64772430049572}
    return pos_boxpol



def plot_radar(bx,by, ax, reproject=False):
    # Plot der Radar Range von Bonn
    import wradlib as wrl
    import numpy as np
    from osgeo import osr
    import matplotlib as mpl

    proj_stereo = wrl.georef.create_osr("dwd-radolan")
    proj_wgs = osr.SpatialReference()
    proj_wgs.ImportFromEPSG(4326)
    x_loc, y_loc = (bx, by)

    r = np.arange(1, 101) * 1000
    # azimuth array 1 degree spacing
    az = np.linspace(0, 360, 361)[0:-1]

    # build polygons for maxrange rangering
    polygons = wrl.georef.polar2polyvert(r, az,
                                         (x_loc, y_loc))
    polygons.shape = (len(az), len(r), 5, 2)
    polygons = polygons[:, -1, :, :]



    if reproject:
        # reproject to radolan polar stereographic projection
        polygons = wrl.georef.reproject(polygons,
                                        projection_source=proj_wgs,
                                        projection_target=proj_stereo)

        # reproject lonlat radar location coordinates to
        # polar stereographic projection
        x_loc, y_loc = wrl.georef.reproject(x_loc, y_loc,
                                            projection_source=proj_wgs,
                                            projection_target=proj_stereo)


    # create PolyCollections and add to respective axes
    polycoll = mpl.collections.PolyCollection(polygons, closed=True,
                                              edgecolors='r',
                                              facecolors='r',
                                              zorder=2)
    ax.add_collection(polycoll, autolim=True)

    # plot radar location and information text
    ax.plot(x_loc, y_loc, 'r+')
    #ax.text(x_loc, y_loc, 'Bonn', color='r')


def cut_the_swath(gprof_lon, gprof_lat, gprof_pp,eu=False):
    # Zurechtschneiden des Scanpfades ueber Deutschland

    import numpy as np

    # Rand bestimmt nach Radolan Eckpunkten

    bonn_lat1 = 46.952580411190304
    bonn_lat2 = 54.896591448461479
    bonn_lon1 = 2.0735617005681379
    bonn_lon2 = 15.704155593113517


    if eu==True:
        bonn_lat1 = 43.874791353919626
        bonn_lat2 = 57.100558552767012
        bonn_lon1 = -0.86239071542899981
        bonn_lon2 = 21.680045338521435

    ilat= np.where((gprof_lat>bonn_lat1) & (gprof_lat<bonn_lat2))
    ilon= np.where((gprof_lon>bonn_lon1) & (gprof_lon<bonn_lon2))
    #lonstart = ilon[0][0]
    #lonend = ilon[0][-1]
    latstart = ilat[0][0]
    latend = ilat[0][-1]


    alon = gprof_lon[latstart:latend]
    alat = gprof_lat[latstart:latend]
    gprof_pp_a = gprof_pp[latstart:latend]


    ailat= np.where((alat>bonn_lat1) & (alat<bonn_lat2))
    ailon= np.where((alon>bonn_lon1) & (alon<bonn_lon2))
    alonstart = ailon[0][0]
    alonend = ailon[0][-1]
    #alatstart = ailat[0][0]
    #alatend = ailat[0][-1]

    blon = alon[alonstart:alonend]
    blat = alat[alonstart:alonend]
    gprof_pp_b = gprof_pp_a[alonstart:alonend]

    return blon, blat, gprof_pp_b


def get_miub_cmap():
    import matplotlib.colors as col
    startcolor = 'white'  # a dark olive
    color1 = '#8ec7ff'#'cyan'    # a bright yellow
    color2 = 'dodgerblue'
    color3 = 'lime'
    color4 = 'yellow'
    color5 = 'darkorange'
    color6 = 'red'
    color7 = 'purple'
    #color6 = 'grey'
    endcolor = 'darkmagenta'    # medium dark red
    colors = [startcolor, color1, color2, color3, color4, color5, color6, endcolor]
    return col.LinearSegmentedColormap.from_list('miub1',colors)

def get_3_cmap():
    import matplotlib.colors as col
    startcolor = 'red'
    color1 = 'cyan'
    endcolor = 'grey'#'red'
    colors = [startcolor, color1,endcolor]
    return col.LinearSegmentedColormap.from_list('3',colors)

def get_4_cmap():
    import matplotlib.colors as col
    startcolor = 'white'
    color1 = 'blue'
    color2 = 'red'
    endcolor = 'grey'#'red'
    colors = [startcolor, color1, color2, endcolor]
    return col.LinearSegmentedColormap.from_list('4',colors)

def get_my_cmap():
    import matplotlib.cm as cm
    my_cmap = cm.get_cmap('jet',40)
    my_cmap.set_under('lightgrey')
    my_cmap.set_over('darkred')
    return my_cmap



def pcc_plot_cg_rhi(data, r=None, th=None, th_res=None, autoext=True, refrac=True,
                rf=1., fig=None, subplot=111, **kwargs):

    import numpy as np
    from wradlib import georef as georef
    import wradlib as wrl

    # autogenerate axis dimensions
    if r is None:
        d1 = np.arange(data.shape[1], dtype=np.float)
    else:
        d1 = np.asanyarray(r)

    if th is None:
        # assume, data is evenly spaced between 0 and 90 degree
        d2 = np.linspace(0., 90., num=data.shape[0], endpoint=True)
        # d2 = np.arange(data.shape[0], dtype=np.float)
    else:
        d2 = np.asanyarray(th)

    if autoext:
        # extend the range by the delta of the two last bins
        x = np.append(d1, d1[-1] + d1[-1] - d1[-2])
        # RHIs usually aren't cyclic, so we best guess a regular extension
        # here as well
        y = np.append(d2, d2[-1] + d2[-1] - d2[-2])
    else:
        # hopefully, the user supplied everything correctly...
        x = d1
        y = d2

    if th_res is not None:
        # we are given a beam resolution and thus may not just glue each
        # beam to its neighbor
        # solving this still with the efficient pcolormesh but interlacing
        # the data with masked values, simulating the gap between beams
        # make a temporary data array with one dimension twice the size of
        # the original
        img = np.ma.empty((data.shape[0], data.shape[1] * 2))
        # mask everything
        img.mask = np.ma.masked
        # set the data in the first half of the temporary array
        # this automatically unsets the mask
        img[:, :data.shape[1]] = data
        # reshape so that data and masked lines interlace each other
        img = img.reshape((-1, data.shape[1]))
        # produce lower and upper y coordinates for the actual data
        yl = d2 - th_res * 0.5
        yu = d2 + th_res * 0.5
        # glue them together to achieve the proper dimensions for the
        # interlaced array
        y = np.concatenate([yl[None, :], yu[None, :]], axis=0).T.ravel()
    else:
        img = data

    # create curvelinear axes
    cgax, caax, paax = wrl.vis.create_cg('RHI', fig, subplot)

    # this is in fact the outermost thick "ring" aka max_range
    cgax.axis["lon"] = cgax.new_floating_axis(1, np.max(x) / rf)
    cgax.axis["lon"].major_ticklabels.set_visible(False)
    # and also set tickmarklength to zero for better presentation
    cgax.axis["lon"].major_ticks.set_ticksize(0)

    if refrac:
        # observing air refractivity, so ground distances and beam height
        # must be calculated specially
        # create coordinates for all vertices
        xx, yy = np.meshgrid(x, y)
        xxx = georef.arc_distance_n(xx, yy) / rf
        yyy = georef.beam_height_n(xx, yy) / rf
        # assign twin-axis/cartesian-axis as plotting axis
        plax = caax
    else:
        # otherwise plotting to parasite axis will do
        # create meshgrid for polar data
        # please note that the data is plottet within a polar grid
        # with 0 degree at 3 o'clock, hence the slightly other data handling
        xxx, yyy = np.meshgrid(y, x)
        yyy /= rf
        img = img.transpose()
        # assign parasite axis as plotting axis
        plax = paax

    # plot the stuff
    pm = plax.pcolormesh(xxx, yyy, img, **kwargs)

    # set bounds to maximum
    cgax.set_ylim(0, np.max(x) / rf)
    cgax.set_xlim(0, np.max(x) / rf)

    # show curvelinear and cartesian grids
    # makes no sense not to plot, if we made such a fuss to get that handled
    cgax.grid(True)
    caax.grid(True)

    # return references to important and eventually new objects
    return cgax, caax, paax, pm, xxx, yyy


def search_nearest(arry,value):
    import numpy as np
    arry_res = arry.reshape(arry.shape[0]* arry.shape[1])
    next = np.argmin(np.abs(np.subtract(arry_res,value)))
    near = np.where(arry == arry_res[next])
    return near


def cut_the_swath2(gprof_lon, gprof_lat, gprof_pp,eu=False):
    # Zurechtschneiden des Scanpfades ueber Deutschland

    import numpy as np

    # Rand bestimmt nach Radolan Eckpunkten

    bonn_lat1 =47
    bonn_lat2 = 54.0
    bonn_lon1 = 4.5
    bonn_lon2 = 14.6


    if eu==True:
        bonn_lat1 = 44
        bonn_lat2 = 55
        bonn_lon1 = 1
        bonn_lon2 = 19

    ilat = np.where(((gprof_lat[:,[0,-1]] > bonn_lat1) )
                   & ((gprof_lat[:,[0,-1]] < bonn_lat2) ))

    latstart = ilat[0][0]
    latend = ilat[0][-1]

    print latstart,' : ',latend

    alon = gprof_lon[latstart:latend]
    alat = gprof_lat[latstart:latend]
    gprof_pp_a = gprof_pp[latstart:latend]


    ailon= np.where(((alon[:,0] > bonn_lon1) & (alon[:,-1] > bonn_lon1))
                    & ((alon[:,0] < bonn_lon2) & (alon[:,-1] < bonn_lon2)))

    alonstart = ailon[0][0]
    alonend = ailon[0][-1]

    print alonstart,' : ',alonend

    blon = alon[alonstart:alonend]
    blat = alat[alonstart:alonend]
    gprof_pp_b = gprof_pp_a[alonstart:alonend]

    return blon, blat, gprof_pp_b


def cut_the_swath3(gx, gy, gg):
    # Zurechtschneiden des Scanpfades ueber Deutschland

    bonn_lat1 =47
    bonn_lat2 = 54.0
    bonn_lon1 = 4.5
    bonn_lon2 = 14.6

    gg[gy < bonn_lat1]=np.nan
    gg[gy > bonn_lat2]=np.nan
    gg[gx > bonn_lon2]=np.nan
    gg[gx < bonn_lon1]=np.nan

    return gx, gy, gg




def alpha_shape(points, alpha):
    from shapely.ops import cascaded_union, polygonize
    from scipy.spatial import Delaunay
    import numpy as np
    import math
    import shapely.geometry as geometry
    """
    Compute the alpha shape (concave hull) of a set
    of points.
    @param points: Iterable container of points.
    @param alpha: alpha value to influence the
        gooeyness of the border. Smaller numbers
        don't fall inward as much as larger numbers.
        Too large, and you lose everything!
    """
    if len(points) < 4:
        # When you have a triangle, there is no sense
        # in computing an alpha shape.
        return geometry.MultiPoint(list(points)).convex_hull

    def add_edge(edges, edge_points, coords, i, j):
        """
        Add a line between the i-th and j-th points,
        if not in the list already
        """
        if (i, j) in edges or (j, i) in edges:
                # already added
            return
        edges.add( (i, j) )
        edge_points.append(coords[ [i, j] ])
    coords = np.array([point.coords[0]
                       for point in points])
    tri = Delaunay(coords)
    edges = set()
    edge_points = []
    # loop over triangles:
    # ia, ib, ic = indices of corner points of the
    # triangle
    for ia, ib, ic in tri.vertices:
        pa = coords[ia]
        pb = coords[ib]
        pc = coords[ic]
        # Lengths of sides of triangle
        a = math.sqrt((pa[0]-pb[0])**2 + (pa[1]-pb[1])**2)
        b = math.sqrt((pb[0]-pc[0])**2 + (pb[1]-pc[1])**2)
        c = math.sqrt((pc[0]-pa[0])**2 + (pc[1]-pa[1])**2)
        # Semiperimeter of triangle
        s = (a + b + c)/2.0
        # Area of triangle by Heron's formula
        area = math.sqrt(s*(s-a)*(s-b)*(s-c))
        circum_r = a*b*c/(4.0*area)
        # Here's the radius filter.
        #print circum_r
        if circum_r < 1.0/alpha:
            add_edge(edges, edge_points, coords, ia, ib)
            add_edge(edges, edge_points, coords, ib, ic)
            add_edge(edges, edge_points, coords, ic, ia)
    m = geometry.MultiLineString(edge_points)
    triangles = list(polygonize(m))
    return cascaded_union(triangles), edge_points

def get_time_of_gpm(gpm_lon, gpm_lat, gpm_time):
    #Todo: Verbesser Momentan Mitte von Swath in RADOLAN, Besser Mitte oder auch ausenpunkte
    mitte = gpm_lon.shape[1]/2 # midel swath
    ii = np.where(((gpm_lon[:,mitte]<15) & (gpm_lon[:,mitte]>2)) & ((gpm_lat[:,mitte]<54) & (gpm_lat[:,mitte] > 46)))
    gpm_year = int(np.median(np.array(gpm_time['Year'])[ii]))
    gpm_month = int(np.median(np.array(gpm_time['Month'])[ii]))
    gpm_day = int(np.median(np.array(gpm_time['DayOfMonth'])[ii]))
    gpm_hour = int(np.median(np.array(gpm_time['Hour'])[ii]))
    gpm_min = int(np.median(np.array(gpm_time['Minute'])[ii]))
    gpm_sek = int(np.median(np.array(gpm_time['Second'])[ii]))
    gpm_dt = dt.datetime(gpm_year,gpm_month, gpm_day, gpm_hour, gpm_min, gpm_sek).strftime("%Y.%m.%d -- %H:%M:%S")
    return gpm_dt


def plot_scatter(est, ref):
    import matplotlib.pyplot as plt
    from scipy import stats
    maske = ~np.isnan(est) & ~np.isnan(ref)
    slope, intercept, r_value, p_value, std_err = stats.linregress(est[maske], ref[maske])
    line = slope * est +intercept

    from pcc import skill_score
    SS = skill_score(est,ref,th=0)

    plt.scatter(est, ref, label='Reflectivity [dBZ]', color='grey', alpha=0.6)

    text = ('f(x) = ' + str(round(slope,3)) + 'x + ' + str(round(intercept,3)) +
               '\nCorr: ' + str(round(r_value,3)) + r'$\pm$: '+  str(round(std_err,3))+
            '\nN: '+ str(int(SS['N']))+
            '\nHit: ' + str(round(SS['H']/SS['N'],3)*100)+'%'+
            '\nMiss: ' + str(round(SS['M']/SS['N'],3)*100)+'%'+
            '\nFalse: ' + str(round(SS['F']/SS['N'],3)*100)+'%'+
            '\nCnegative: ' + str(round(SS['C']/SS['N'],3)*100)+'%'+
            '\nHR: ' + str(round(SS['HR'],3))+
            '\nPOD: ' + str(round(SS['POD'],3))+
            '\nFAR: ' + str(round(SS['FAR'],3))+
            '\nBID: ' + str(round(SS['BID'],3))+
            '\nHSS: ' + str(round(SS['HSS'],3))+
            '\nBias: '+ str(round(SS['bias'],3))+
            '\nRMSE: '+ str(round(SS['RMSE'],3))
            )

    plt.annotate(text, xy=(0.01, 0.99), xycoords='axes fraction', fontsize=10,
                    horizontalalignment='left', verticalalignment='top')

    t1 = np.linspace(0,70,70)
    plt.plot(t1,t1,'k-')
    plt.plot(t1, t1*slope + intercept, 'r-', lw=3 ,label='Regression')
    plt.plot(t1, t1*slope + (intercept+5), 'r-.', lw=1.5 ,label=r'Reg $\pm$ 5 mdBZ')
    plt.plot(t1, t1*slope + (intercept-5), 'r-.', lw=1.5 )
    plt.plot(np.nanmean(est),np.nanmean(ref), 'ob', lw = 4,label='Mean')

    plt.legend(loc='lower right', fontsize=10, scatterpoints= 1, numpoints=1, shadow=True)
    plt.xlim(0,70)
    plt.ylim(0,70)


def melde_dich(text):
    import smtplib

    me = 'velibor.pejcic@gmx.de'
    you = 'velibor.pejcic@gmx.de'

    # Import the email modules we'll need
    from email.mime.text import MIMEText

    # Open a plain text file for reading.  For this example, assume that
    # the text file contains only ASCII characters.
    fp = open('/home/velibor/shkgpm/texte/t1', 'rb')
    # Create a text/plain message
    msg = MIMEText(fp.read())
    fp.close()

    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = text
    msg['From'] = me
    msg['To'] = you

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('localhost')
    s.sendmail(me, [you], msg.as_string())
    s.quit()

#Farbe und schrifftart
#print '\033[92m'+'Hi'
#color ende
#print '\033[0m'+'Hi'
def farbig(stringi, farbe):

    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    farben = {'purple': PURPLE, 'cyan':CYAN, 'darkcyan':DARKCYAN, 'blue':BLUE,
              'green': GREEN, 'red': RED, 'bold':BOLD, 'underline': UNDERLINE}

    return farben[farbe] + stringi + END
