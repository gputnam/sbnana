# branches for the new CAF structure
mchdrbranches = [
    "rec.hdr.pot",
    "rec.hdr.first_in_subrun",
    "rec.hdr.ismc",
    "rec.hdr.run",
    "rec.hdr.subrun",
    "rec.hdr.ngenevt",
    "rec.hdr.evt",
    "rec.hdr.proc",
    "rec.hdr.cluster",
    "rec.hdr.fno",
]

hdrbranches = [
    "rec.hdr.pot",
    "rec.hdr.first_in_subrun",
    "rec.hdr.ismc",
    "rec.hdr.run",
    "rec.hdr.subrun",
    "rec.hdr.ngenevt",
    "rec.hdr.evt",
    "rec.hdr.proc",
    "rec.hdr.cluster",
    "rec.hdr.fno",

    # "rec.hdr.triggerinfo.trigger_id",
    # "rec.hdr.triggerinfo.gate_id",
    # "rec.hdr.triggerinfo.trigger_count",
    # "rec.hdr.triggerinfo.gate_count",
    # "rec.hdr.triggerinfo.gate_delta",
    # "rec.hdr.triggerinfo.global_trigger_time",
    # "rec.hdr.triggerinfo.prev_global_trigger_time",
]

potbranches = [
    "rec.hdr.numiinfo.spill_time_s",
    "rec.hdr.numiinfo.spill_time_ns",
    "rec.hdr.numiinfo.TRTGTD",
    "rec.hdr.numiinfo.TORTGT",
    "rec.hdr.numiinfo.daq_gates",
]

trueparticlenames = [
    "start_process",
    "end_process",
    "pdg",
    "startE",
    "start.x", "start.y", "start.z",
    "end.x", "end.y", "end.z",
    "genp.x", "genp.y", "genp.z",
    "length",
    "G4ID",
    "parent",
    "cont_tpc",
    "genE",
    "interaction_id",
    "startp.x", "startp.y", "startp.z",
    "endp.x", "endp.y", "endp.z",
]

trueparticlebranches = ["rec.true_particles.%s" % s for s in trueparticlenames]

pfpbranch = "rec.slc.reco.pfp."
trkbranch = pfpbranch + "trk."
shwbranch = pfpbranch + "shw."

pfobranches = [
    pfpbranch + "pfochar.chgendfrac",
    pfpbranch + "pfochar.chgfracspread",
    pfpbranch + "pfochar.linfitdiff",
    pfpbranch + "pfochar.linfitlen",
    pfpbranch + "pfochar.linfitgaplen",
    pfpbranch + "pfochar.linfitrms",
    pfpbranch + "pfochar.openanglediff",
    pfpbranch + "pfochar.pca2ratio",
    pfpbranch + "pfochar.pca3ratio", 
    pfpbranch + "pfochar.vtxdist" 
]

pfpbranches = [
    pfpbranch + "parent_is_primary",
    pfpbranch + "slcID",
    pfpbranch + "trackScore",
    pfpbranch + "parent",
    pfpbranch + "id",
    pfpbranch + "t0",
    pfpbranch + "ndaughters",
] #+ pfobranches

pfp_daughter_branch = [
    pfpbranch + "daughters"
]

trkbranches = [
    trkbranch + "producer",
    trkbranch + "start.x", trkbranch + "start.y", trkbranch + "start.z",
    trkbranch + "end.x", trkbranch + "end.y", trkbranch + "end.z",
    trkbranch + "dir.x", trkbranch + "dir.y", trkbranch + "dir.z",
    trkbranch + "phi", trkbranch + "costh",
    trkbranch + "len",
    trkbranch + "rangeP.p_muon",
    trkbranch + "mcsP.fwdP_muon",
    trkbranch + "mcsP.bwdP_muon",
    trkbranch + "mcsP.is_bwd_muon",
    trkbranch + "rangeP.p_pion",
    trkbranch + "mcsP.fwdP_pion",
    trkbranch + "rangeP.p_proton",
    trkbranch + "mcsP.fwdP_proton",
    trkbranch + "bestplane",
    trkbranch + "dazzle.bestScore",
    trkbranch + "dazzle.muonScore",
    trkbranch + "dazzle.otherScore",
    trkbranch + "dazzle.pdg",
    trkbranch + "dazzle.pionScore",
    trkbranch + "dazzle.protonScore",
    trkbranch + "chi2pid.2.pid_ndof",
    trkbranch + "chi2pid.2.chi2_kaon", trkbranch + "chi2pid.2.chi2_muon", trkbranch + "chi2pid.2.chi2_pion", trkbranch + "chi2pid.2.chi2_proton",
    trkbranch + "chi2pid.1.chi2_kaon", trkbranch + "chi2pid.1.chi2_muon", trkbranch + "chi2pid.1.chi2_pion", trkbranch + "chi2pid.1.chi2_proton",
    trkbranch + "chi2pid.0.chi2_kaon", trkbranch + "chi2pid.0.chi2_muon", trkbranch + "chi2pid.0.chi2_pion", trkbranch + "chi2pid.0.chi2_proton",
    ]

trkmcsbranches = [
  trkbranch + "mcsP.seg_length",
  trkbranch + "mcsP.seg_scatter_angles",
]

shwbranches = [
  shwbranch + "len"
]

trkhitadcbranches = [
  trkbranch + "calo.2.points.adcs"
]

trkhitbranches_perplane = lambda IPLANE : [
    trkbranch + "calo.%i.points.dedx"% IPLANE,
    trkbranch + "calo.%i.points.dqdx"% IPLANE,
    trkbranch + "calo.%i.points.pitch"% IPLANE,
    trkbranch + "calo.%i.points.integral"% IPLANE,
    trkbranch + "calo.%i.points.rr"% IPLANE,
    trkbranch + "calo.%i.points.wire"% IPLANE,
    trkbranch + "calo.%i.points.tpc"% IPLANE,
    trkbranch + "calo.%i.points.sumadc"% IPLANE,
    trkbranch + "calo.%i.points.t"% IPLANE,
    trkbranch + "calo.%i.points.x"% IPLANE,
    trkbranch + "calo.%i.points.y"% IPLANE,
    trkbranch + "calo.%i.points.z"% IPLANE,

    #trkbranch + "calo.%i.points.width"% IPLANE,
    #trkbranch + "calo.%i.points.mult"% IPLANE,
    #trkbranch + "calo.%i.points.tdc0"% IPLANE,

    trkbranch + "calo.%i.points.truth.h_e"% IPLANE,
    trkbranch + "calo.%i.points.truth.h_nelec"% IPLANE,
    trkbranch + "calo.%i.points.truth.pitch"% IPLANE,
    trkbranch + "calo.%i.points.truth.rr"% IPLANE,
]

trkhitbranches = trkhitbranches_perplane(2)
trkhitbranches_P1 = trkhitbranches_perplane(1)
trkhitbranches_P0 = trkhitbranches_perplane(0)

for n in trueparticlenames: trkbranches.append(trkbranch + "truth.p." + n)

slcbranches = [
    "rec.slc.is_clear_cosmic",
    "rec.slc.vertex.x", "rec.slc.vertex.y", "rec.slc.vertex.z",
    "rec.slc.self",
    "rec.slc.tmatch.eff", "rec.slc.tmatch.pur", "rec.slc.tmatch.index",
    "rec.slc.producer",
    "rec.slc.charge",
    "rec.slc.truth.pdg",
    "rec.slc.nu_score",
    "rec.slc.fmatch.score", "rec.slc.fmatch.time",
	"rec.slc.crumbs_result.score",
    "rec.slc.nuid.crlongtrkdiry"
	]

mcbranches = [
    "rec.mc.nu.E",
    'rec.mc.nu.time',
    'rec.mc.nu.bjorkenX', 
    'rec.mc.nu.inelasticityY',
    'rec.mc.nu.Q2', 
    'rec.mc.nu.q0', 
    'rec.mc.nu.q0_lab',
    'rec.mc.nu.t', 
    'rec.mc.nu.w', 
    "rec.mc.nu.momentum.x",
    "rec.mc.nu.momentum.y",
    "rec.mc.nu.momentum.z",
    "rec.mc.nu.position.x",
    "rec.mc.nu.position.y",
    "rec.mc.nu.position.z",
    "rec.mc.nu.pdg",
    "rec.mc.nu.iscc",
    "rec.mc.nu.genie_mode",
    "rec.mc.nu.genie_inttype",
    'rec.mc.nu.nneutron', 'rec.mc.nu.npiminus', 'rec.mc.nu.npiplus', 'rec.mc.nu.npizero', 'rec.mc.nu.nproton', 
    'rec.mc.nu.nprim',
    'rec.mc.nu.genweight',
    'rec.mc.nu.parent_dcy_mode',
    'rec.mc.nu.parent_pdg',
    ]

mcprimbranches = [
    'rec.mc.nu.prim.pdg', 
    'rec.mc.nu.prim.startE',
    'rec.mc.nu.prim.genE',
    'rec.mc.nu.prim.start.x', 'rec.mc.nu.prim.start.y', 'rec.mc.nu.prim.start.z',
    'rec.mc.nu.prim.end.x','rec.mc.nu.prim.end.y','rec.mc.nu.prim.end.z',
    'rec.mc.nu.prim.startp.x','rec.mc.nu.prim.endp.x',
    'rec.mc.nu.prim.startp.y','rec.mc.nu.prim.endp.y',
    'rec.mc.nu.prim.startp.z', 'rec.mc.nu.prim.endp.z',
    'rec.mc.nu.prim.end_process', 'rec.mc.nu.prim.start_process'
    ]

slc_mcbranches = ["rec.slc.truth." + ".".join(s.split(".")[3:]) for s in mcbranches]
slc_mcprimbranches = ["rec.slc.truth." + ".".join(s.split(".")[3:]) for s in mcprimbranches]

stubbranches = [
    "rec.slc.reco.stub.vtx.x",
    "rec.slc.reco.stub.vtx.y",
    "rec.slc.reco.stub.vtx.z",
    "rec.slc.reco.stub.end.x",
    "rec.slc.reco.stub.end.y",
    "rec.slc.reco.stub.end.z",
    "rec.slc.reco.stub.efield_vtx",
    "rec.slc.reco.stub.efield_end",
    "rec.slc.reco.stub.pfpid",
    "rec.slc.reco.stub.truth.p.pdg",
    "rec.slc.reco.stub.truth.p.genE",
    "rec.slc.reco.stub.truth.p.interaction_id",
]

stubplanebranches = [
    "rec.slc.reco.stub.planes.p",
    "rec.slc.reco.stub.planes.hit_w",
    "rec.slc.reco.stub.planes.vtx_w",
    "rec.slc.reco.stub.planes.pitch",
    "rec.slc.reco.stub.planes.trkpitch",
]

stubhitbranches = [
    "rec.slc.reco.stub.planes.hits.charge",
    "rec.slc.reco.stub.planes.hits.ontrack",
    "rec.slc.reco.stub.planes.hits.wire",
]
