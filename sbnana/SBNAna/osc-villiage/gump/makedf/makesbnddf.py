from pyanalib.panda_helpers import *
from .branches import *
from .util import *
from . import numisyst, g4syst, geniesyst
import uproot

PROTON_MASS = 0.938272
MUON_MASS = 0.105658
PION_MASS = 0.139570

DETECTOR = "SBND"
if DETECTOR == "SBND":
    alpha_sbnd = 0.930                                                                                                                                             
    LAr_density_gmL_sbnd = 1.38434                                                                                                                                             
    Efield_sbnd = 0.5                                                                                                                                              
    beta_sbnd = 0.212 / (LAr_density_gmL_sbnd * Efield_sbnd)                                                                                                                             
    Wion = 1e3 / 4.237e7                                                                                                                                      


def make_hdrdf(f):
    hdr = loadbranches(f["recTree"], hdrbranches).rec.hdr
    return hdr

def make_mchdrdf(f):
    hdr = loadbranches(f["recTree"], mchdrbranches).rec.hdr
    return hdr

def make_potdf(f):
    pot = loadbranches(f["recTree"], potbranches).rec.hdr.numiinfo
    return pot

def make_mcnuwgtdf(f):
    return make_mcnudf(f, include_weights=True)

def make_mcnudf(f, include_weights=False):
    mcdf = make_mcdf(f)
    mcdf["ind"] = mcdf.index.get_level_values(1)
    if include_weights:
        wgtdf = pd.concat([numisyst.numisyst(mcdf.pdg, mcdf.E), geniesyst.geniesyst(f, mcdf.ind), g4syst.g4syst(f, mcdf.ind)], axis=1)
        mcdf = multicol_concat(mcdf, wgtdf)
    return mcdf

def make_mchdf(f, include_weights=False):
    mcdf = loadbranches(f["recTree"], mchbranches).rec.mc.prtl
    if include_weights:
        wgtdf = numisyst.numisyst(14, mcdf.E) # TODO: what PDG?
        mcdf = pd.concat([mcdf, wgtdf], axis=1)
    return mcdf

def make_trkdf(f, scoreCut=False, requiret0=False, requireCosmic=False, recalo=True, mcs=True):
    trkdf = loadbranches(f["recTree"], trkbranches + shwbranches)
    if scoreCut:
        trkdf = trkdf.rec.slc.reco[trkdf.rec.slc.reco.pfp.trackScore > 0.5]
    else:
        trkdf = trkdf.rec.slc.reco

    if requiret0:
        trkdf = trkdf[~np.isnan(trkdf.pfp.t0)]

    if requireCosmic:
        trkdf = trkdf[trkdf.pfp.parent == -1]

    if mcs:
        mcsdf = loadbranches(f["recTree"], [trkmcsbranches[0]]).rec.slc.reco.pfp.trk.mcsP
        mcsdf_angle = loadbranches(f["recTree"], [trkmcsbranches[1]]).rec.slc.reco.pfp.trk.mcsP
        mcsdf_angle.index.set_names(mcsdf.index.names, inplace=True)

        mcsdf = mcsdf.merge(mcsdf_angle, how="left", left_index=True, right_index=True)
        mcsgroup = list(range(mcsdf.index.nlevels-1))
        cumlen = mcsdf.seg_length.groupby(level=mcsgroup).cumsum()*14 # convert rad length to cm
        maxlen = (cumlen*(mcsdf.seg_scatter_angles >= 0)).groupby(level=mcsgroup).max()
        trkdf[("pfp", "trk", "mcsP", "len", "", "")] = maxlen


    trkdf[("pfp", "tindex", "", "", "", "")] = trkdf.index.get_level_values(2)

    return trkdf

def make_trkhitdf(f):
    df = loadbranches(f["recTree"], trkhitbranches).rec.slc.reco.pfp.trk.calo.I2.points

    # Firsthit and Lasthit info
    ihit = df.index.get_level_values(-1)
    df["firsthit"] = ihit == 0

    lasthit = df.groupby(level=list(range(df.index.nlevels-1))).tail(1).copy()
    lasthit["lasthit"] = True
    df["lasthit"] = lasthit.lasthit
    df.lasthit = df.lasthit.fillna(False)

    return df

def make_slcdf(f):
    slcdf = loadbranches(f["recTree"], slcbranches)
    slcdf = slcdf.rec

    slc_mcdf = make_mcdf(f, slc_mcbranches, slc_mcprimbranches)
    slc_mcdf.columns = pd.MultiIndex.from_tuples([tuple(["slc", "truth"] + list(c)) for c in slc_mcdf.columns])
    slcdf = multicol_merge(slcdf, slc_mcdf, left_index=True, right_index=True, how="left", validate="one_to_one")

    return slcdf

def make_mcdf(f, branches=mcbranches, primbranches=mcprimbranches):
    # load the df
    mcdf = loadbranches(f["recTree"], branches)
    while mcdf.columns.nlevels > 2:
        mcdf.columns = mcdf.columns.droplevel(0)

    # Add in primary particle info
    mcprimdf = loadbranches(f["recTree"], primbranches)
    while mcprimdf.columns.nlevels > 2:
        mcprimdf.columns = mcprimdf.columns.droplevel(0)

    mcprimdf.index = mcprimdf.index.rename(mcdf.index.names[:2] + mcprimdf.index.names[2:])

    max_proton_KE = mcprimdf[np.abs(mcprimdf.pdg)==2212].genE.groupby(level=[0,1]).max() - PROTON_MASS
    max_proton_KE.name = ("max_proton_ke", "")
    mcdf = mcdf.join(max_proton_KE)

    mcdf.max_proton_ke = mcdf.max_proton_ke.fillna(0.)

    # particle counts
    mcdf = mcdf.join((np.abs(mcprimdf.pdg)==2112).groupby(level=[0,1]).sum().rename(("nn", "")))
    mcdf = mcdf.join((np.abs(mcprimdf.pdg)==2212).groupby(level=[0,1]).sum().rename(("np", "")))
    mcdf = mcdf.join((np.abs(mcprimdf.pdg)==13).groupby(level=[0,1]).sum().rename(("nmu", "")))
    mcdf = mcdf.join((np.abs(mcprimdf.pdg)==211).groupby(level=[0,1]).sum().rename(("npi", "")))
    mcdf = mcdf.join((np.abs(mcprimdf.pdg)==111).groupby(level=[0,1]).sum().rename(("npi0", "")))
    mcdf = mcdf.join((np.abs(mcprimdf.pdg)==22).groupby(level=[0,1]).sum().rename(("ng", "")))
    mcdf = mcdf.join((np.abs(mcprimdf.pdg)==321).groupby(level=[0,1]).sum().rename(("nk", "")))
    mcdf = mcdf.join((np.abs(mcprimdf.pdg)==310).groupby(level=[0,1]).sum().rename(("nk0", "")))
    mcdf = mcdf.join((np.abs(mcprimdf.pdg)==3112).groupby(level=[0,1]).sum().rename(("nsm", "")))
    mcdf = mcdf.join((np.abs(mcprimdf.pdg)==3222).groupby(level=[0,1]).sum().rename(("nsp", "")))

    # particle counts w/ threshold
    proton_KE = mcprimdf[np.abs(mcprimdf.pdg)==2212].genE - PROTON_MASS
    muon_KE = mcprimdf[np.abs(mcprimdf.pdg)==13].genE - MUON_MASS
    pion_KE = mcprimdf[np.abs(mcprimdf.pdg)==211].genE - PION_MASS
    mcdf = mcdf.join(((np.abs(mcprimdf.pdg)==2212) & (proton_KE > 0.05)).groupby(level=[0,1]).sum().rename(("np_50MeV","")))
    mcdf = mcdf.join(((np.abs(mcprimdf.pdg)==2212) & (proton_KE > 0.02)).groupby(level=[0,1]).sum().rename(("np_20MeV","")))
    mcdf = mcdf.join(((np.abs(mcprimdf.pdg)==13) & (muon_KE > 0.02)).groupby(level=[0,1]).sum().rename(("nmu_20MeV","")))
    mcdf = mcdf.join(((np.abs(mcprimdf.pdg)==211) & (pion_KE > 0.04)).groupby(level=[0,1]).sum().rename(("npi_40MeV","")))

    # lepton info
    mudf = mcprimdf[np.abs(mcprimdf.pdg)==13].sort_values(mcprimdf.index.names[:2] + [("genE", "")]).groupby(level=[0,1]).last()
    mudf.columns = pd.MultiIndex.from_tuples([tuple(["mu"] + list(c)) for c in mudf.columns])

    pdf = mcprimdf[mcprimdf.pdg==2212].sort_values(mcprimdf.index.names[:2] + [("genE", "")]).groupby(level=[0,1]).last()
    pdf.columns = pd.MultiIndex.from_tuples([tuple(["p"] + list(c)) for c in pdf.columns])

    mcdf = multicol_merge(mcdf, mudf, left_index=True, right_index=True, how="left", validate="one_to_one")
    mcdf = multicol_merge(mcdf, pdf, left_index=True, right_index=True, how="left", validate="one_to_one")

    return mcdf

def make_slc_trkdf(f, trkScoreCut=False, trkDistCut=10., cutClearCosmic=True, **trkArgs):
    # load
    trkdf = make_trkdf(f, trkScoreCut, **trkArgs)
    slcdf = make_slcdf(f)

    # merge in tracks
    slcdf = multicol_merge(slcdf, trkdf, left_index=True, right_index=True, how="right", validate="one_to_many")

    # distance from vertex to track start
    slcdf = multicol_add(slcdf, dmagdf(slcdf.slc.vertex, slcdf.pfp.trk.start).rename(("pfp", "dist_to_vertex")))

    if trkDistCut > 0:
        slcdf = slcdf[slcdf.pfp.dist_to_vertex < trkDistCut]
    if cutClearCosmic:
        slcdf = slcdf[slcdf.slc.is_clear_cosmic==0]

    return slcdf

def make_eslc_partdf(f, trkDistCut=-1, **trkArgs):
    # load
    partdf = make_epartdf(f, **trkArgs)
    partdf.columns = pd.MultiIndex.from_tuples([tuple(["particle"] + list(c)) for c in partdf.columns])
    eslcdf = make_eslcdf(f)

    # merge in tracks
    eslcdf = multicol_merge(eslcdf, partdf, left_index=True, right_index=True, how="right", validate="one_to_many")
    eslcdf = multicol_add(eslcdf, dmagdf(eslcdf.vertex, eslcdf.particle.start_point).rename("dist_to_vertex"))

    if trkDistCut > 0:
        eslcdf = eslcdf[eslcdf.dist_to_vertex < trkDistCut]

    return eslcdf

def make_stubs(f):
    stubdf = loadbranches(f["recTree"], stubbranches)
    stubdf = stubdf.rec.slc.reco.stub

    stubpdf = loadbranches(f["recTree"], stubplanebranches)
    stubpdf = stubpdf.rec.slc.reco.stub.planes

    stubdf["nplane"] = stubpdf.groupby(level=[0,1,2]).size()
    stubdf["plane"] = stubpdf.p.groupby(level=[0,1,2]).first()

    stubhitdf = loadbranches(f["recTree"], stubhitbranches)
    stubhitdf = stubhitdf.rec.slc.reco.stub.planes.hits

    stubhitdf = stubhitdf.join(stubpdf)
    stubhitdf = stubhitdf.join(stubdf.efield_vtx)
    stubhitdf = stubhitdf.join(stubdf.efield_end)

    hdrdf = make_mchdrdf(f)
    ismc = hdrdf.ismc.iloc[0]
    def dEdx2dQdx_mc(dEdx): # MC parameters
        if DETECTOR == "SBND":
            return np.log(alpha_sbnd + dEdx*beta_sbnd) / (Wion*beta_sbnd)
        beta = MODB_mc / (LAr_density_gmL_mc * Efield_mc)
        alpha = MODA_mc
        return np.log(alpha + dEdx*beta) / (Wion*beta)
    def dEdx2dQdx_data(dEdx): # data parameters
        if DETECTOR == "SBND":
            return np.log(alpha_sbnd + dEdx*beta_sbnd) / (Wion*beta_sbnd)
        beta = MODB_data / (LAr_density_gmL_data * Efield_data)
        alpha = MODA_data
        return np.log(alpha + dEdx*beta) / (Wion*beta)

    dEdx2dQdx = dEdx2dQdx_mc if ismc else dEdx2dQdx_data
    MIP_dqdx = dEdx2dQdx(1.7) 

    stub_end_charge = stubhitdf.charge[stubhitdf.wire == stubhitdf.hit_w].groupby(level=[0,1,2,3]).first().groupby(level=[0,1,2]).first()
    stub_end_charge.name = ("endp_charge", "", "")

    stub_pitch = stubpdf.pitch.groupby(level=[0,1,2]).first()
    stub_pitch.name = ("pitch", "", "")

    stubdir_is_pos = (stubhitdf.hit_w - stubhitdf.vtx_w) > 0.
    when_sum = ((stubhitdf.wire > stubhitdf.vtx_w) == stubdir_is_pos) & (((stubhitdf.wire < stubhitdf.hit_w) == stubdir_is_pos) | (stubhitdf.wire == stubhitdf.hit_w)) 
    stubcharge = (stubhitdf.charge[when_sum]).groupby(level=[0,1,2,3]).sum().groupby(level=[0,1,2]).first()
    stubcharge.name = ("charge", "", "")

    stubinccharge = (stubhitdf.charge).groupby(level=[0,1,2,3]).sum().groupby(level=[0,1,2]).first()
    stubinccharge.name = ("inc_charge", "", "")

    hit_before_start = ((stubhitdf.wire < stubhitdf.vtx_w) == stubdir_is_pos)
    stub_inc_sub_charge = (stubhitdf.charge - MIP_dqdx*stubhitdf.ontrack*(~hit_before_start)*stubhitdf.trkpitch).groupby(level=[0,1,2,3]).sum().groupby(level=[0,1,2]).first()
    stub_inc_sub_charge.name = ("inc_sub_charge", "", "")

    stubdf = stubdf.join(stubcharge)
    stubdf = stubdf.join(stubinccharge)
    stubdf = stubdf.join(stub_inc_sub_charge)
    stubdf = stubdf.join(stub_end_charge)
    stubdf = stubdf.join(stub_pitch)
    stubdf["length"] = magdf(stubdf.vtx - stubdf.end)
    stubdf["Q"] = stubdf.inc_sub_charge

    # convert charge to energy
    if ismc:
        stubdf["ke"] = Q2KE_mc(stubdf.Q)
        # also do calorimetric variations
        stubdf["ke_callo"] = Q2KE_mc_callo(stubdf.Q)
        stubdf["ke_calhi"] = Q2KE_mc_calhi(stubdf.Q)
    else:
        stubdf["ke"] = Q2KE_data(stubdf.Q)
        stubdf["ke_callo"] = np.nan
        stubdf["ke_calhi"] = np.nan

    stubdf.ke = stubdf.ke.fillna(0)
    stubdf.Q = stubdf.Q.fillna(0)

    stubdf["dedx"] = stubdf.ke / stubdf.length
    stubdf["dedx_callo"] = stubdf.ke_callo / stubdf.length
    stubdf["dedx_calhi"] = stubdf.ke_calhi / stubdf.length

    # only take collection plane
    stubdf = stubdf[stubdf.plane == 2]

    stub_length_bins = [0, 0.5, 1, 2, 3]
    stub_length_name = ["l0_5cm", "l1cm", "l2cm", "l3cm"]
    tosave = ["dedx", "dedx_callo", "dedx_calhi", "Q", "length", "charge", "inc_charge"] 

    df_tosave = []
    for blo, bhi, name in zip(stub_length_bins[:-1], stub_length_bins[1:], stub_length_name):
        stub_tosave = stubdf.dedx[(stubdf.length > blo) & (stubdf.length < bhi)].groupby(level=[0,1]).idxmax()
        for col in tosave:
            s = stubdf.loc[stub_tosave, col]
            s.name = ("stub", name, col, "", "", "")
            s.index = s.index.droplevel(-1)
            df_tosave.append(s)

    return pd.concat(df_tosave, axis=1)

def make_eslcdf(f):
    eslcdf = loadbranches(f["recTree"], eslcbranches)
    eslcdf = eslcdf.rec.dlp

    etintdf = loadbranches(f["recTree"], etruthintbranches)
    etintdf = etintdf.rec.dlp_true
    
    # match to the truth info
    mcdf = make_mcdf(f)
    # mc is truth
    mcdf.columns = pd.MultiIndex.from_tuples([tuple(["truth"] + list(c)) for c in mcdf.columns])

    # Do matching
    # 
    # First get the ML true particle IDs matched to each reco particle
    eslc_matchdf = loadbranches(f["recTree"], eslcmatchedbranches)
    eslc_match_overlap_df = loadbranches(f["recTree"], eslcmatchovrlpbranches)
    eslc_match_overlap_df.index.names = eslc_matchdf.index.names

    eslc_matchdf = multicol_merge(eslc_matchdf, eslc_match_overlap_df, left_index=True, right_index=True, how="left", validate="one_to_one")
    eslc_matchdf = eslc_matchdf.rec.dlp

    # Then use bestmatch.match to get the nu ids in etintdf
    eslc_matchdf_wids = pd.merge(eslc_matchdf, etintdf, left_on=["entry", "match"], right_on=["entry", "id"], how="left")
    eslc_matchdf_wids.index = eslc_matchdf.index

    # Now use nu_ids to get the true interaction information
    eslc_matchdf_trueints = multicol_merge(eslc_matchdf_wids, mcdf, left_on=["entry", "nu_id"], right_index=True, how="left")
    eslc_matchdf_trueints.index = eslc_matchdf_wids.index

    # delete unnecesary matching branches
    del eslc_matchdf_trueints[("match", "")]
    del eslc_matchdf_trueints[("nu_id", "")]
    del eslc_matchdf_trueints[("id", "")]

    # first match is best match
    bestmatch = eslc_matchdf_trueints.groupby(level=list(range(eslc_matchdf_trueints.index.nlevels-1))).first()

    # add extra levels to eslcdf columns
    eslcdf.columns = pd.MultiIndex.from_tuples([tuple(list(c) + [""]*2) for c in eslcdf.columns])

    eslcdf_withmc = multicol_merge(eslcdf, bestmatch, left_index=True, right_index=True, how="left")

    # Fix position names (I0, I1, I2) -> (x, y, z)
    def mappos(s):
        if s == "I0": return "x"
        if s == "I1": return "y"
        if s == "I2": return "z"
        return s
    def fixpos(c):
        if c[0] not in ["end_point", "start_point", "start_dir", "vertex", "momentum"]: return c
        return tuple([c[0]] + [mappos(c[1])] + list(c[2:]))

    eslcdf_withmc.columns = pd.MultiIndex.from_tuples([fixpos(c) for c in eslcdf_withmc.columns])

    return eslcdf_withmc

def make_epartdf(f):
    epartdf = loadbranches(f["recTree"], eparticlebranches)
    epartdf = epartdf.rec.dlp.particles

    tpartdf = loadbranches(f["recTree"], trueparticlebranches)
    tpartdf = tpartdf.rec.true_particles
    # cut out EMShowerDaughters
    # tpartdf = tpartdf[(tpartdf.parent == 0)]

    etpartdf = loadbranches(f["recTree"], etrueparticlebranches)
    etpartdf = etpartdf.rec.dlp_true.particles
    etpartdf.columns = [s for s in etpartdf.columns]
    
    # Do matching
    # 
    # First get the ML true particle IDs matched to each reco particle
    epart_matchdf = loadbranches(f["recTree"], eparticlematchedbranches)
    epart_match_overlap_df = loadbranches(f["recTree"], eparticlematchovrlpbranches)
    epart_match_overlap_df.index.names = epart_matchdf.index.names
    epart_matchdf = multicol_merge(epart_matchdf, epart_match_overlap_df, left_index=True, right_index=True, how="left", validate="one_to_one")
    epart_matchdf = epart_matchdf.rec.dlp.particles
    # get the best match (highest match_overlap), assume it's sorted
    bestmatch = epart_matchdf.groupby(level=list(range(epart_matchdf.index.nlevels-1))).first()
    bestmatch.columns = [s for s in bestmatch.columns]

    # Then use betmatch.match to get the G4 track IDs in etpartdf
    bestmatch_wids = pd.merge(bestmatch, etpartdf, left_on=["entry", "match"], right_on=["entry", "id"], how="left")
    bestmatch_wids.index = bestmatch.index

    # Now use the G4 track IDs to get the true particle information
    bestmatch_trueparticles = multicol_merge(bestmatch_wids, tpartdf, left_on=["entry", "track_id"], right_on=["entry", ("G4ID", "")], how="left")
    bestmatch_trueparticles.index = bestmatch_wids.index

    # delete unnecesary matching branches
    del bestmatch_trueparticles[("match", "")]
    del bestmatch_trueparticles[("track_id", "")]
    del bestmatch_trueparticles[("id", "")]

    # add extra level to epartdf columns
    epartdf.columns = pd.MultiIndex.from_tuples([tuple(list(c) + [""]) for c in epartdf.columns])

    # put everything in epartdf
    for c in bestmatch_trueparticles.columns:
        epartdf[tuple(["truth"] + list(c))] = bestmatch_trueparticles[c]

    # Fix position names (I0, I1, I2) -> (x, y, z)
    def mappos(s):
        if s == "I0": return "x"
        if s == "I1": return "y"
        if s == "I2": return "z"
        return s
    def fixpos(c):
        if c[0] not in ["end_point", "start_point", "start_dir", "vertex"]: return c
        return tuple([c[0]] + [mappos(c[1])] + list(c[2:]))

    epartdf.columns = pd.MultiIndex.from_tuples([fixpos(c) for c in epartdf.columns])

    return epartdf

def make_trkdf(f, scoreCut=False, requiret0=False, requireCosmic=False, recalo=True, mcs=True):
    trkdf = loadbranches(f["recTree"], trkbranches + shwbranches)
    if scoreCut:
        trkdf = trkdf.rec.slc.reco[trkdf.rec.slc.reco.pfp.trackScore > 0.5]
    else:
        trkdf = trkdf.rec.slc.reco

    if requiret0:
        trkdf = trkdf[~np.isnan(trkdf.pfp.t0)]

    if requireCosmic:
        trkdf = trkdf[trkdf.pfp.parent == -1]

    if mcs:
        mcsdf = loadbranches(f["recTree"], [trkmcsbranches[0]]).rec.slc.reco.pfp.trk.mcsP
        mcsdf_angle = loadbranches(f["recTree"], [trkmcsbranches[1]]).rec.slc.reco.pfp.trk.mcsP
        mcsdf_angle.index.set_names(mcsdf.index.names, inplace=True)

        mcsdf = mcsdf.merge(mcsdf_angle, how="left", left_index=True, right_index=True)
        mcsgroup = list(range(mcsdf.index.nlevels-1))
        cumlen = mcsdf.seg_length.groupby(level=mcsgroup).cumsum()*14 # convert rad length to cm
        maxlen = (cumlen*(mcsdf.seg_scatter_angles >= 0)).groupby(level=mcsgroup).max()
        trkdf[("pfp", "trk", "mcsP", "len", "", "")] = maxlen


    trkdf[("pfp", "tindex", "", "", "", "")] = trkdf.index.get_level_values(2)

    return trkdf

def make_eevtdf(f):
    # load slices and particles
    partdf = make_epartdf(f)

    df = make_eslcdf(f)

    # load the proton and muon candidates
    primary = partdf.is_primary
    mudf = partdf[primary & (partdf.pid == 2)].sort_values(partdf.index.names[:2] + [("length", "", "")]).groupby(level=[0,1]).last()
    mudf.columns = pd.MultiIndex.from_tuples([tuple(["mu"] + list(c)) for c in mudf.columns])

    pdf = partdf[primary & (partdf.pid == 4)].sort_values(partdf.index.names[:2] + [("length", "", "")]).groupby(level=[0,1]).last()
    pdf.columns = pd.MultiIndex.from_tuples([tuple(["p"] + list(c)) for c in pdf.columns])

    df = multicol_merge(df, mudf, left_index=True, right_index=True, how="left", validate="one_to_one")
    df = multicol_merge(df, pdf, left_index=True, right_index=True, how="left", validate="one_to_one")

    # in case we want to cut out other objects -- save the highest energy of each other particle
    lead_gamma_energy = partdf.ke[primary & (partdf.pid == 0)].groupby(level=[0,1]).max().rename("lead_gamma_energy")
    df = multicol_add(df, lead_gamma_energy)

    lead_elec_energy = partdf.ke[primary & (partdf.pid == 1)].groupby(level=[0,1]).max().rename("lead_elec_energy")
    df = multicol_add(df, lead_elec_energy)

    lead_pion_length = partdf.length[primary & (partdf.pid == 3)].groupby(level=[0,1]).max().rename("lead_pion_length")
    df = multicol_add(df, lead_pion_length)

    subl_muon_length = partdf[primary & (partdf.pid == 2)].sort_values(partdf.index.names[:2] + [("length", "", "")]).length.groupby(level=[0,1]).nth(-2).rename("subl_muon_length")
    df = multicol_add(df, subl_muon_length)

    subl_proton_length = partdf[primary & (partdf.pid == 4)].sort_values(partdf.index.names[:2] + [("length", "", "")]).length.groupby(level=[0,1]).nth(-2).rename("subl_proton_length")
    df = multicol_add(df, subl_proton_length)

    # Apply pre-selection: Require fiducial vertex, at least one muon, at least one proton

    # require both muon and proton to be present
    df = df[~np.isnan(df.mu.pid) & ~np.isnan(df.p.pid)]

    # require fiducial verex
    df = df[InFV(df.vertex, 50)]

    return df


def make_evtdf_sbnd(f):

    # mcdf = make_mcdf(f)
    slcdf = make_slc_trkdf(f)

    # PID
    ts_cut = (slcdf.pfp.trackScore > 0.5)

    pid_shw = np.invert(ts_cut)

    # muon
    MUSEL_MUSCORE_TH = 25
    MUSEL_PSCORE_TH = 100
    MUSEL_LEN_TH = 50

    # TODO: used BDT scores
    # muon_chi2 = (Avg(df, "muon", drop_0=True) < MUSEL_MUSCORE_TH) & (Avg(df, "proton", drop_0=True) > MUSEL_PSCORE_TH)
    # len_cut = (masterdf.len.squeeze() > MUSEL_LEN_TH)
    # dazzle_muon = (masterdf.dazzle.muonScore > 0.6)
    # muon_cut = (muon_chi2) & (len_cut | dazzle_muon)

    mu_score_cut = (slcdf.pfp.trk.chi2pid.I2.chi2_muon < MUSEL_MUSCORE_TH) & \
        (slcdf.pfp.trk.chi2pid.I2.chi2_proton > MUSEL_PSCORE_TH)
    mu_len_cut = (slcdf.pfp.trk.len > MUSEL_LEN_TH)
    mu_cut = (mu_score_cut) & (mu_len_cut)
    pid_mu = (ts_cut) & (mu_cut)

    # proton 
    PSEL_MUSCORE_TH = 0
    PSEL_PSCORE_TH = 90
    p_score_cut = (slcdf.pfp.trk.chi2pid.I2.chi2_muon > PSEL_MUSCORE_TH) & (slcdf.pfp.trk.chi2pid.I2.chi2_muon < PSEL_PSCORE_TH) 
    p_cut = np.invert(mu_cut) & p_score_cut
    pid_p = (ts_cut) & (p_cut)

    # rest is pion
    pi_cut = np.invert(mu_cut | p_cut)
    pid_pi = (ts_cut) & (pi_cut)

    # TODO: don't use trackscore

    # ---------------------------

    # store PID info
    slcdf[("pfp", "pid", "", "", "", "")] = np.nan
    slcdf.loc[pid_shw, ("pfp","pid")] = -1
    slcdf.loc[pid_mu, ("pfp","pid")] = 13
    slcdf.loc[pid_p, ("pfp","pid")] = 2212
    slcdf.loc[pid_pi, ("pfp","pid")] = 211

    mudf = slcdf[(slcdf.pfp.pid == 13)].sort_values(slcdf.pfp.index.names[:-1] + [("pfp", "trk", "len", "", "", "")]).groupby(level=[0,1,2]).last()
    mudf.columns = pd.MultiIndex.from_tuples([tuple(["mu"] + list(c)) for c in mudf.columns])
    
    pdf = slcdf[(slcdf.pfp.pid == 2212)].sort_values(slcdf.pfp.index.names[:-1] + [("pfp", "trk", "len", "", "", "")]).groupby(level=[0,1,2]).last()
    pdf.columns = pd.MultiIndex.from_tuples([tuple(["p"] + list(c)) for c in pdf.columns])
    
    slcdf = multicol_merge(slcdf, mudf, left_index=True, right_index=True, how="left", validate="one_to_one")
    slcdf = multicol_merge(slcdf, pdf, left_index=True, right_index=True, how="left", validate="one_to_one")
    
    # in case we want to cut out other objects -- save the highest energy of each other particle
    lead_shw_length = slcdf.pfp.trk.len[(slcdf.pfp.pid < 0)].groupby(level=[0,1,2]).max().rename("lead_shw_length")
    slcdf = multicol_add(slcdf, lead_shw_length)
    
    lead_pion_length = slcdf.pfp.trk.len[(slcdf.pfp.pid == 211)].groupby(level=[0,1,2]).max().rename("lead_pion_length")
    slcdf = multicol_add(slcdf, lead_pion_length)
    
    subl_muon_length = slcdf[(slcdf.pfp.pid == 13)].sort_values(slcdf.pfp.index.names[:-1] + [("pfp", "trk", "len", "", "", "")]).pfp.trk.len.groupby(level=[0,1,2]).nth(-2).rename("subl_muon_length")
    slcdf = multicol_add(slcdf, subl_muon_length)
    
    subl_proton_length = slcdf[(slcdf.pfp.pid == 2212)].sort_values(slcdf.pfp.index.names[:-1] + [("pfp", "trk", "len", "", "", "")]).pfp.trk.len.groupby(level=[0,1,2]).nth(-2).rename("subl_proton_length")
    slcdf = multicol_add(slcdf, subl_proton_length)

    return slcdf

