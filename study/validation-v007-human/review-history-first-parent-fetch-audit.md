# Calibration review-history first-parent fetch audit

Execution: **FETCH**
Result: **PASS**

Only exact first-parent links for repositories in the frozen calibration split are considered. Fetches deepen the exact target commit by one parent with `--no-tags --no-write-fetch-head --deepen=1 --filter=tree:0`; no branch or tag ref is fetched or updated. Git receives the missing first-parent commit and minimal tree support objects, not a repository snapshot or file blobs.

## Population

- Calibration review/history source occurrences: 335
- Missing-parent occurrences: 296
- Total diff-required occurrences: 218
- Diff-required occurrences still excluded by a missing parent: 193
- Unique target commits in calibration repos: 133
- Parent objects present before this execution: 16
- Parent objects missing before this execution: 117
- Parent links already resolvable before this execution: 10
- Repositories needing one-commit deepen: 123
- Successfully fetched and verified in this execution: 123
- Already connected: 10
- Failed/verification issues: 0

## Per-commit results

| Repository | Target commit | First parent | Required findings | Parent object present | Link resolved before | Status | Verified | Refs unchanged | Worktree unchanged |
|---|---|---|---:|---|---|---|---|---|---|
| `ARTbio/GalaxyKickStart` | `d04bc40174594a2996a23a1c1b07155de4a694e4` | `5441dbf6cb82428ad257216896571bda1e231561` | 3 | True | True | already-connected | True | True | True |
| `Ableton/ansible-role-jenkins-jcasc` | `a62ef61b70877018fb6763b17f7d29a771fbc597` | `b257eb541a5d202c7954053f6c649fd586ae6468` | 1 | False | False | fetched | True | True | True |
| `ArkCase/arkcase-ce` | `75895cbe09118f02addf4c00fd8e10b8ccddeaa8` | `cc8bfa96dbae2c1b6abdd490e4f9c746d0897851` | 1 | False | False | fetched | True | True | True |
| `AtlasOfLivingAustralia/ala-install` | `aa2070a840f5debc3b78095c31b58004d04d2063` | `d9628f4674332a869eee790c46c6533f0c3c203f` | 1 | False | False | fetched | True | True | True |
| `CMSgov/bluebutton-web-deployment` | `ef2da5200c4d70c9db49e682ae28cd52ca92c995` | `7b51c2c8a691e22742517d395df865589c778802` | 3 | True | True | already-connected | True | True | True |
| `Checkmk/ansible-collection-checkmk.general` | `50be8bde935f94e4702f40c9a549f86ffe773db1` | `b20471273d6a9d616e0c1a2c03a9252291764350` | 1 | False | False | fetched | True | True | True |
| `ClarifiedSecurity/catapult` | `b299a088ed596b9dfc9b6241c837eb1a227c567c` | `004cd8466e7ca4863e09771979a14dc7f25027fb` | 3 | False | False | fetched | True | True | True |
| `ComplianceAsCode/content` | `30d390c4b0d1f842a87a16d953c584e213cef4d5` | `0bf797af9844aa0be772cde9bb427ab1e6cefd77` | 1 | False | False | fetched | True | True | True |
| `Everpure-Ansible/FlashArray-Collection` | `db7927a407849f14f929ca0e15b247821b529b3d` | `90300e6cc971bfc2b1fe2904cc71119f42f89848` | 1 | False | False | fetched | True | True | True |
| `FreiFunkMuenster/Ansible-Freifunk-Gateway` | `b04e8f81b2b010eaccd13a63271c7ce7eb6fb4b3` | `e6fe3df6fde0ed01cd473de2e3035f16e5271e25` | 2 | False | False | fetched | True | True | True |
| `IAreKyleW00t/k2net` | `63cf522a122691ae38ec90146c10a6d332231d00` | `39f8914235f7ea69befca1666c14df76dedeaf65` | 3 | False | False | fetched | True | True | True |
| `IBM/ibm-spectrum-scale-install-infra` | `6e9fdebea0d9a7e66563ea3595d9eff160986d25` | `99c63c980f58850c1c7dd4d41b9523138513f650` | 3 | True | True | already-connected | True | True | True |
| `IDR/deployment` | `77f7a7e438a41ca775e85b629c0f84cc636ffad7` | `f7e2258900faa2d643e5e3749c1140c9e96c7ba6` | 2 | True | True | already-connected | True | True | True |
| `JenswBE/setup` | `18c39275cc08ae3f7bea8b7ee0624876b8fa72fe` | `e5da41a552dec21a6da8e80066a6a8a05107707e` | 3 | False | False | fetched | True | True | True |
| `Kubeinit/kubeinit` | `da6fec314d5594b6bd97ef2e4e71f9098a85e63c` | `b5af1c00b5de2dbdb09b7078927047cb52b71823` | 1 | False | False | fetched | True | True | True |
| `Linuxfabrik/lfops` | `9b51b59db61b87e01cc75adef892e5345a5bf4b1` | `a06df86264ee7649865c83b846a50a1e742d6ad1` | 1 | False | False | fetched | True | True | True |
| `ManageIQ/manageiq` | `dce1a2757a633d3902a2e3af1b8faf9e9f91ed3c` | `f757c193498aa62348573213dd2d28d735369460` | 2 | False | False | fetched | True | True | True |
| `NLNOG/ring-ansible` | `b8a7aede6730b3fa3fc3065e187ace979ceedd01` | `cb61b29cfd06b76fbd32f609cf2b27dc66f430f6` | 3 | False | False | fetched | True | True | True |
| `NSLS2/nsls2.ioc_deploy` | `10518de6b2fbd124ce01d7b67512558f3bcf7b8e` | `0a87f86ed000cf53aec83b12691ace9d3cb4f59a` | 1 | False | False | fetched | True | True | True |
| `NationalGenomicsInfrastructure/miarka-provision` | `52daa7027450753c62cb0f38a2b5ef546cae7ede` | `87fd063d27a9a83e06bfab9b8454ef4564297a2d` | 3 | False | False | fetched | True | True | True |
| `O-X-L/ansible-opnsense` | `4f4acafcb5b6bd21886645e3ab0c530d8f0b25f1` | `92f510c0f4ac020fb4dbc839bb9828e7ee7c6465` | 1 | False | False | fetched | True | True | True |
| `Princeton-CDH/cdh-ansible` | `8fc536c88cbc18d048418263ecc64a9b1c339922` | `0272d1862246083b5f20c57354892523331df773` | 1 | False | False | fetched | True | True | True |
| `RedHatGov/redhatgov.workshops` | `c946ce095cafcf55bb14a465932410419dac34f2` | `57573bc3544bc34aed1ec484e7879ca2e5820350` | 1 | False | False | fetched | True | True | True |
| `Sunbird-Obsrv/sunbird-data-pipeline` | `eb1e1a1c3533c549693dda32cd92c667754aaea9` | `c56f74d01d9c3ab12650ecdbb03718add736cf79` | 1 | False | False | fetched | True | True | True |
| `TechDufus/dotfiles` | `abe3beabdf436c1a7aeeff66b6c2f5903f7b9878` | `56a0085acb2bc4f835ce6f20aa7a1fe5a80ecc16` | 1 | False | False | fetched | True | True | True |
| `UtrechtUniversity/yoda` | `a9175010319fee30fb056665e9821937f0ec07c5` | `e753902d3440cc8b083d6e9a49b86f81c32d17fb` | 3 | False | False | fetched | True | True | True |
| `adoptium/infrastructure` | `d31f47293b3a0166a4f9d7b8c51475d548999408` | `eaa867066e164f4eda7c81c59e20f0f09a286e14` | 1 | False | False | fetched | True | True | True |
| `anokfireball/homelab-as-code` | `d8fe576217e433a746fff052b772c949ee6f1e50` | `d371518856de2d89500dd808191ad60078947bb2` | 3 | False | False | fetched | True | True | True |
| `ansible-collections/amazon.aws` | `f9a2dc6670a088ea5119d3e93a5dcd99a3753bfe` | `4406e626a9fd56bf9fddc6621ef8c2b1bc700022` | 1 | False | False | fetched | True | True | True |
| `ansible-collections/azure` | `45e49bd7cc781b6324b2c726ea5cde3cbe1d0f93` | `38a4eb536cab6ebdd087c1c4e4090b86b74d3c1b` | 1 | False | False | fetched | True | True | True |
| `ansible-collections/community.general` | `60972bc7422ba42060695353ecb54a7c5a99eef0` | `375183709e2b73e879ac0e0dbb31f66d8e39536a` | 1 | False | False | fetched | True | True | True |
| `ansible-collections/community.vmware` | `f8fde60167ae8f6d252d46691913f7a451e2d723` | `b594e9b0f995586f253c7554de5d565398578fe2` | 1 | False | False | fetched | True | True | True |
| `ansible-collections/ibm_zos_core` | `f0cc9ddc4402424c1f91d920ca9455d4133c9d21` | `c01e440b54ade23aca84842319421880dc7716a6` | 1 | False | False | fetched | True | True | True |
| `ansible-lockdown/RHEL7-STIG` | `a3d78cfc5c2cae8f8b344fbcd6664a35817dbad0` | `00d0839d8ee1a1233299aec1bc6e9aa4797d5f0b` | 3 | False | False | fetched | True | True | True |
| `ansible-lockdown/RHEL8-CIS` | `97a6a9aa80506900009129aa389759d6884d5ec5` | `c80dcc55fe35c053364a0230313adb3bacb1b00e` | 1 | False | False | fetched | True | True | True |
| `ansible-lockdown/RHEL8-STIG` | `baa075468dfa59050141c99d99dcacd2e977248c` | `4eb768f63d1bc3f2c4935b8634ed3ae1603b4a43` | 1 | False | False | fetched | True | True | True |
| `ansible-network/windmill-config` | `91d52c11ec5492688d64cac9100a6a7a7e120793` | `ada35201cd9aa1bb1fcf5cb67e10264c944dcc94` | 1 | False | False | fetched | True | True | True |
| `ansible/awx` | `54d6e576fb543c76f672603ca7f26913d58cf458` | `b33640096308c4987f94212bb77e2c4f9691c1ef` | 1 | False | False | fetched | True | True | True |
| `ansible/awx-operator` | `45363a1a0d312d16f740c626407a7521bbe3a31c` | `0a548a5731b8a41612498449de8c29338dcd8e0e` | 1 | False | False | fetched | True | True | True |
| `ansible/galaxy-operator` | `a05c8663b7e5cf4c2350fb1faa074a378b86f0fc` | `57db029642630990f318be8e6873e876356ec951` | 1 | False | False | fetched | True | True | True |
| `ansible/instruqt` | `e23435acd50f1f645c88958c8dee4fe2929014b6` | `b7515564a6252638b7f1a9fcb6b20ba3241aac3b` | 1 | False | False | fetched | True | True | True |
| `ansible/vscode-ansible` | `a63dab35a4c1c530142bc1f29fb7c03bacb46578` | `e49e195f4841c6213997f176ea20fb00f627119b` | 1 | False | False | fetched | True | True | True |
| `ansible/zuul-config` | `82f3415452ef899524f4257b3cdae20b13692c87` | `48416f8cb10c14d9450bb4272ffb043273333b13` | 1 | False | False | fetched | True | True | True |
| `anthonymolinari/ansible-gitops` | `61aa79a0c1f6641317187d3a7afec6b6c4d54a5f` | `615d2465b7edaba70395155801a353567ed9d09e` | 3 | False | False | fetched | True | True | True |
| `aristanetworks/avd` | `05092c872036e7e90e1b4986cbfb2b36798c5a4d` | `a7a626fddd4cf7a34ef9208c06986f6a6774f8fb` | 1 | False | False | fetched | True | True | True |
| `autobase-tech/autobase` | `f24ff3d316e688901a1118a9f769798f40dd42e7` | `f5bd2def352d816358972b9e74f7437109534385` | 1 | False | False | fetched | True | True | True |
| `axivo/k3s-cluster` | `f0e3a56f57f0e13f9f8624af2bb370c7eb92063f` | `ef403a1bc013889894bad38e28f93e1a2e6ff5d9` | 3 | False | False | fetched | True | True | True |
| `azimuth-cloud/ansible-collection-azimuth-ops` | `396972118edcecb213e69497f9f2c70e7abd0611` | `dfea757a4f909cfab387d0217b609ad487603e89` | 3 | False | False | fetched | True | True | True |
| `bluebanquise/bluebanquise` | `fcc5b8776f3b1bde7ca4fba65b8cb2e77617f7b0` | `18226e54464846436801dd3dbe23589034965b28` | 3 | False | False | fetched | True | True | True |
| `braucktoon/home-services-ansible-automation` | `47b8b32d5d23ac4f319eb42ada558173ddae47c1` | `89466777e733cb59d4dca09aa8b9ac02c74aff76` | 3 | False | False | fetched | True | True | True |
| `carnivuth/labcraft` | `3547209dd2823344c728f8054eff0074675e6558` | `64a190c3cb15ed29816c2e32296165770255e65d` | 3 | False | False | fetched | True | True | True |
| `cfpb/aurora` | `03e01e4bd080040159dd089175179ef3c6baa3e3` | `b63d613368d8aa4c4715797a2b85f4dc27da51d2` | 2 | True | True | already-connected | True | True | True |
| `chkpwd/iac` | `9b789a76960f81aa13ecdb2c29fbcb799b5e4fcf` | `a8b03ef1a51e85d1f82a535b7b15d6be69691dc7` | 3 | False | False | fetched | True | True | True |
| `chrisshaiman/lamware` | `09f919635087b38354bce34c9bc48e7c6517b463` | `b027b6c7406fde2f6adfe2dae735708013cab6cf` | 1 | False | False | fetched | True | True | True |
| `cisco-en-programmability/dnacenter-ansible` | `33276c6275a666371b085bea241441cf4f6a29d2` | `1f8d2fd798d2c3a2e61d8e0ad9f0b5428adf4425` | 1 | False | False | fetched | True | True | True |
| `clusterinthecloud/ansible` | `a378fceff7cd03dbd36da1fc4bd5a4ed09270c60` | `17a87bf74a952609ef62b7ddc856c215e03b7526` | 1 | False | False | fetched | True | True | True |
| `compscidr/iac` | `350e7b8162778ad7beab8e2da8be53ea24a1127a` | `98c0b334c9eabd7a7135b4f59a512fbee06804a1` | 1 | False | False | fetched | True | True | True |
| `confluentinc/cp-ansible` | `11aa6b84f2ac19da7dc259c23fe854e01a1c5be3` | `237958e3de824644ea5a451ec5506075e20ca6f9` | 1 | False | False | fetched | True | True | True |
| `coolguy1771/home-ops` | `06a34bd98c97519188b586db673a8c3d94f74cfc` | `998f6169e39d591824abb438b8ac644aba77bddc` | 2 | False | False | fetched | True | True | True |
| `cradle8810/ansible_hayaworld` | `d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597` | `8a850ac47ddec1755168470f904e29488e5c572c` | 3 | False | False | fetched | True | True | True |
| `dell/dellemc-openmanage-ansible-modules` | `1f35059202d432465b8bd54e980d069a88583edc` | `c5d4f3a1b6ead19e3090317f19ded0aa70d6daa2` | 1 | False | False | fetched | True | True | True |
| `delphix/appliance-build` | `e6237bbdcc7f3b49d7e053f1dad8800c0b30e4cc` | `3d513689a1ea7d7681fcd286dcdb8a9c698a273c` | 1 | False | False | fetched | True | True | True |
| `dev-sec/ansible-collection-hardening` | `3102eddbd116c5f8c1581aca543d372dbc326764` | `084fe828f6f6cf825b1f4073a34220303f7f7caf` | 1 | False | False | fetched | True | True | True |
| `dfroberg/cluster` | `7bc521db65db986a2deef35ea955704bb0621dbd` | `672177b273c0f1ee86eb804223bfb0f0b5b89a7c` | 1 | False | False | fetched | True | True | True |
| `dimagi/commcare-cloud` | `f184ea5721b60efd0efce1cc96ce251bcf60df08` | `9988e63a5fe0aa2b27c9134020020fa81794edda` | 1 | False | False | fetched | True | True | True |
| `dryvist/ansible-proxmox-apps` | `b179574eb875a6b7be09df83d001f623a68a2681` | `116a5d9ad56e3bff0e8207bebcb86f906965be89` | 1 | False | False | fetched | True | True | True |
| `easzlab/kubeasz` | `fcb46a47a7fcd3bbc97498ea4aefdd564e16b383` | `2547bf30deeb3becbf5630156a9fbcf71a432101` | 1 | False | False | fetched | True | True | True |
| `electrocucaracha/krd` | `fe54e6752bc86b7c23056a15ea70f34d2be5cb33` | `2fa008ded3e92164c3096114a277a5451efb55b0` | 1 | False | False | fetched | True | True | True |
| `ethpandaops/ansible-collection-general` | `15a1f3490258357c4652b96b80f0a92636fa4135` | `75bfdb7bb0f3bcbaeaed44e059ea9abf7ded428f` | 1 | False | False | fetched | True | True | True |
| `eyulf/homelab` | `5cef75d48f9df9a47c8b9fe37f3c20ce7a4d2b91` | `9341beabc050bd3bfcc5b0403415b917b2eacb53` | 3 | False | False | fetched | True | True | True |
| `folio-org/folio-ansible` | `dde7c5f2011b34eb79b03ef38f334b34449e67af` | `489173a71d90df1a901c01c21c1543fd98d1c69f` | 3 | False | False | fetched | True | True | True |
| `freeipa/ansible-freeipa` | `5ba9b59d5b614abdb0af70fc9f2d336e5479e833` | `e37f190ee17ae474e97d17291f9fd583aca6df78` | 1 | True | False | fetched | True | True | True |
| `freifunk-berlin/bbb-configs` | `a504e8298bf12b7ffae09536a6b01841b091c01d` | `d71d13ef11a19ce36ed16687dc10be84c0327742` | 3 | False | False | fetched | True | True | True |
| `gdcc/dataverse-ansible` | `ae29ce65dd4cddd5187c2bc00aefd319b6bb4484` | `39e46d6cd4d1b6a7ba5524c4870352f5aba7cf31` | 1 | False | False | fetched | True | True | True |
| `grycap/im` | `5e54aa6e02108a615abf2670abaa4aa1c56add02` | `b1d00d19de5e900baae3c21b8de59f523a81ff23` | 1 | False | False | fetched | True | True | True |
| `ictsc/ictsc-drove` | `05ebbc720b4b71d5dbe7d1a8da3d617807378cb5` | `1c5b8fc04ec04a91c593405238d9a26115b782bf` | 3 | False | False | fetched | True | True | True |
| `igou-io/igou-ansible` | `5dac3e63735e0e15407c172e0abd56d431fe4e47` | `394515f3c115297150fdcf274161ea411c4cef72` | 1 | False | False | fetched | True | True | True |
| `jlu5/ansible-dn42` | `7849481eec35fe085a7b45d187ed909f356cb8f1` | `a8b18ac537c31b1c62868f9a54e367adbb93a268` | 1 | False | False | fetched | True | True | True |
| `jr0dd/home-ops` | `0e76c37818159bea648890d4ee132616f6ed6499` | `550839c5dc9040f9b5eefe2c48e72dee44d625c4` | 3 | True | False | fetched | True | True | True |
| `konstruktoid/ansible-role-docker-rootless` | `45f43781b7245948eb760a11b5e6648f3106e5ab` | `b3b28f67d5f055c0f30e8c9b154c19256484d0b7` | 1 | False | False | fetched | True | True | True |
| `konstruktoid/ansible-role-hardening` | `4dc09871ed38322eb6e4cdda8e2c77b79892d73d` | `080a77988581818294b130b0637d1324cc72d563` | 1 | False | False | fetched | True | True | True |
| `kubernetes-sigs/kubespray` | `9ee6f9b27981b251d77302fd6cf631f330e0ec39` | `332387f1ab39112a2455fee1ced941dfe0e7fbc7` | 1 | False | False | fetched | True | True | True |
| `kubevirt/project-infra` | `2b204a6ee9bcf983613baf20f122fe2272dbcf3e` | `2ea97322ec0d2faf296585b36eb89caab528ad0a` | 3 | False | False | fetched | True | True | True |
| `ls1intum/artemis-ansible-collection` | `02e584e629e7eda53301159bc2790e45a14f444c` | `e949727e70e5490c36687b06b935880e30a37b63` | 3 | False | False | fetched | True | True | True |
| `mageops/ansible-infrastructure` | `5c612ace8b03fdd369ce0dcdd5e74b638a35f6a8` | `f43dda320ec66d942b01be0511747854d32a9399` | 3 | True | True | already-connected | True | True | True |
| `maksimkurb/home-ops` | `800c51d7a5fb5caa7301e0c221cd04b3bb5daddd` | `9e52f0e69529ae5ba88df4b901d763093b56275d` | 3 | False | False | fetched | True | True | True |
| `manala/ansible-roles` | `1ae6394d7b780665788234418ace2a060903f5f1` | `f2bc5c4c60665fdc1ccaf2d55da0cf3f440c5905` | 2 | True | True | already-connected | True | True | True |
| `michnmi/ansible_internal` | `25f44a7ad44d44b7b91837256958ff443ba28a1e` | `8dc6509a15de1ea16841f9c1415e0ecebd176cd9` | 1 | False | False | fetched | True | True | True |
| `nautobot/nautobot-ansible` | `06a3eb60942b9bbaa9b553503806f8ec7054ba13` | `cc2f0446507579cdcf723a4f3ca7f0eae07d608a` | 1 | True | False | fetched | True | True | True |
| `netbootxyz/netboot.xyz` | `ab7808414f239fc7b582b4c10894fc9b1e246b8f` | `b4b56d6ada9f871cbac6dbf88afe84d8362151aa` | 1 | False | False | fetched | True | True | True |
| `netscaler/ansible-collection-netscaleradc` | `ad99f76947cfdce50b2a6c07bf8800e46209d199` | `968b27b1fd0102f0edf7c332b53a3175f44028e0` | 1 | True | False | fetched | True | True | True |
| `ol3d/home-ops` | `09006fd5ee923e0735b8808865d82fe1b66a2d0c` | `aed7f7e02306639e1ef3d949802627b8438d2a61` | 3 | False | False | fetched | True | True | True |
| `oliversalzburg/ansible-workstation` | `635ab67d1fdf72ea4de69556c8dd428626699df5` | `0e227d759c9dc04956fa36ba20fc85007c2dd409` | 3 | False | False | fetched | True | True | True |
| `ome/prod-playbooks` | `1e935ebbd3344066db3a175fbe4e89c55ffc930b` | `f431e8e5998c8b38084de3c1f7fcb551e1b2e39d` | 2 | True | True | already-connected | True | True | True |
| `openfoodfoundation/ofn-install` | `5e26b29ee7c0eb6ffff54e502b570b4b92e0b7d9` | `91b0c2aa5f8f76583039106a02f77a31fd590c2a` | 1 | False | False | fetched | True | True | True |
| `openstack-k8s-operators/edpm-ansible` | `9d5d672bb0787dc3e8b8ccc829bb101c28e4ee26` | `2b5442cc91e98761e71394d8670a36400444bb63` | 1 | False | False | fetched | True | True | True |
| `os-migrate/os-migrate` | `60e4123dd2391233d23149d7dfb6ebe4b0870590` | `8e232fcf4efd48997f6baf3e706efacfbcb63091` | 1 | False | False | fetched | True | True | True |
| `osism/ansible-collection-services` | `131734f2c007d0009a7fc218849f4ede66c7c899` | `aaa6ce5a4ffd1dbdc5065c87e140ba202b58f848` | 1 | False | False | fetched | True | True | True |
| `osism/testbed` | `ef457f4318fd7f7dce061cafe13159bcbb87f74e` | `f17053bff307199d7fec27623f34a7209bfe6560` | 1 | False | False | fetched | True | True | True |
| `pascaliske/infrastructure` | `ff49a4f405e8ff8200a88c176086dd7a6cdaaf0a` | `ddec8a485316c3b960f1ed0a50db14ecd0c71217` | 3 | False | False | fetched | True | True | True |
| `pjbriggs/ansible-palfinder-galaxy` | `e77a4b2ccc9ade57dcbb71f2c2d3e25db01d2169` | `9bc7994867a88952c299f4005529b9a43aed768f` | 3 | False | False | fetched | True | True | True |
| `plopoyop/ansible-collection-kubernetes_observability` | `9b1eebb1ec42fae20e1688459495285a91bd4dcb` | `b20d1758b779b1f066884ed3ff2c9ea8a7470d23` | 1 | False | False | fetched | True | True | True |
| `prismatic-koi/home-ops` | `9391f2b5ade5539e5411263618b85ef1b52b82c6` | `8dad4871dfff1c842803a6ab890dde4e6481b69b` | 3 | False | False | fetched | True | True | True |
| `pulibrary/princeton_ansible` | `5f01e9a8e80ce332b7c3710302ed1e5af00ebe91` | `b6d0741ffa43058a5f0df568ec2bf95b2281f954` | 1 | False | False | fetched | True | True | True |
| `pulp/pulp_ansible` | `0e0db0f5691bd58361efd90a8b2924474af23a29` | `0bb8069812843661dc162d812f0ffecef6c657e5` | 1 | False | False | fetched | True | True | True |
| `redhat-cop/aap_configuration_extended` | `b58344f735518744459c0501cf8971c0541f0caa` | `ff114380ab33fdd44afabdc00793a38a982ed91f` | 1 | False | False | fetched | True | True | True |
| `redhat-cop/infra.aap_configuration` | `f84d6a61e4b18aa135d707fe539371587bc92931` | `ac57127ee71c8b446f306a3b5deafe3bf6ec6614` | 1 | False | False | fetched | True | True | True |
| `redhatci/ansible-collection-redhatci-ocp` | `4b12e633ee5215ec02c302032fffb3d5f3e37425` | `506def4b64b60ee2d94b68632871128e76abfba9` | 1 | False | False | fetched | True | True | True |
| `ric03uec/clawrium` | `77274d5ca3d71b5a057df332482dd678446d9544` | `40c28d107c65d5808a268f7882bdc33543f83f0b` | 1 | False | False | fetched | True | True | True |
| `ricsanfre/pi-cluster` | `f55c4ba0659fd1409389f39026d91441bb0cf6d0` | `7719c5aacc810fbf2165e5635b4c81a2c90df5b4` | 1 | False | False | fetched | True | True | True |
| `rolehippie/kubetools` | `da7b088b4900cc8763f145a4d71b8b9a917a0d17` | `91070a6ea7998618e19e674973d19692a24d396b` | 1 | False | False | fetched | True | True | True |
| `roots/trellis` | `cd8e671076918a82efb43d5a313451f4e71da318` | `9cf297ea982be995a0bcd8a4cc348a31f7db7f1e` | 1 | True | False | fetched | True | True | True |
| `scruffaluff/bootware` | `f3940d2d3afeead1262403c6087fe598db0d883b` | `2691713d40b77379d3ee64efda4774bba78f9386` | 1 | False | False | fetched | True | True | True |
| `sdwilsh/ansible-playbooks` | `40be40030f481071eceb674509623b21986a04b5` | `a3d030b9b5272322f3f856157ab66a48fc699d50` | 1 | False | False | fetched | True | True | True |
| `seapath/ansible` | `bc10619e516866d0e86af601fd7aa8738b55e645` | `d66eb4cbc0e11c201a16db2c344c2c7969a4bd5c` | 1 | False | False | fetched | True | True | True |
| `sebdanielsson/infra` | `abc768b1d6cd78d1e2feef1262645bb2769fb5df` | `bd80240724f79b5f9ba5eed2aef9ea0634193989` | 3 | False | False | fetched | True | True | True |
| `silogen/cluster-bloom` | `6122fdec7e1e0feed6081e46be0e44cd45d08809` | `76094f22f9870bd46903be58374ca7fa4815316a` | 1 | False | False | fetched | True | True | True |
| `snowdrop/k8s-infra` | `0a9fe0fb57bd9759833bb9974d5022d945b2647c` | `22fb940695f4b7b73a39936f6b75011e0c8ea3fa` | 1 | True | False | fetched | True | True | True |
| `spantaleev/matrix-docker-ansible-deploy` | `8309e7932dd995f83fb022d646fe4b1c4f2a9d98` | `af213b353377fe8eb566f192f9d9cdafcad365ad` | 1 | False | False | fetched | True | True | True |
| `stackhpc/ansible-slurm-appliance` | `f49fc24f6818ea960a28aa2e41910532c86214f9` | `454bf9405c64fc9c1156820cd82cb6855ad48ac7` | 1 | False | False | fetched | True | True | True |
| `stackhpc/stackhpc-release-train` | `3d2f5ac77d3aee42d3c2f206811a7eb8244c55f8` | `a5a05fea6a35826a15f21fd496447a8c90d8171b` | 3 | False | False | fetched | True | True | True |
| `theforeman/foreman-ansible-modules` | `6c08783ce38b1dd35fc28e2754b2d11ebf508d95` | `26f948f56a13f2a087bdd5e6ef31bd648a1cd1c8` | 1 | False | False | fetched | True | True | True |
| `theforeman/forklift` | `ee24dec347fc0a785d22989fd1a183393fa4e054` | `e4826a994ca0c5697fd66ed41141ea4d8b0730d1` | 1 | False | False | fetched | True | True | True |
| `theopenlab/openlab-zuul-jobs` | `0d133dc0879296c0aacd0b70344515c94137a8ec` | `dfa694b78c95cb8bc86d35257f4a40679d23c77d` | 3 | False | False | fetched | True | True | True |
| `trailofbits/algo` | `20e22a8715c198b38c01c1ca62d0953b93587a74` | `5799195c4a0ba065bdb2c766533068228bc3253e` | 1 | False | False | fetched | True | True | True |
| `usegalaxy-eu/infrastructure-playbook` | `13681d4e758b42aeeb7e12aac62243e76a5c04fb` | `09e6f2de3ace4721d5a320500ce3de567c655f5d` | 1 | False | False | fetched | True | True | True |
| `usegalaxy-eu/vgcn` | `c65e4ea9febe2bf5eeca04715c93a441d82f7875` | `9cf0572aeae5ce57b1771eb35b2bac46c792bf27` | 2 | True | True | already-connected | True | True | True |
| `vladgh/ansible-collection-vladgh-system` | `30ae05e5841fd001f70b3b80be8ea029f454e1f7` | `ad7b24ff066ca0c3ad780b9028c0a41bad510d27` | 1 | False | False | fetched | True | True | True |
| `vndmtrx/k8s-in-a-box` | `1031c616283a0badf1f94e3716cd8c7d91e0f972` | `4952a193a79d3da438148603ed92ea2e7e310ae1` | 3 | False | False | fetched | True | True | True |
| `vrk-kpa/api-catalog` | `e81b1cb5a261a290a78eafae67f853efc8f5f7a3` | `6c78cf4bc143d18a69641861689b2b1e2e3e265a` | 3 | True | True | already-connected | True | True | True |
| `waifulabs/infrastructure` | `4700ccdac2f33d386aba763fa03940ac2a25b7ee` | `ca77575628a1d73e2c71441e702c74eae214ac3e` | 2 | False | False | fetched | True | True | True |
| `wonderbird/ansible-all-my-things` | `4993019d9dfb175eef6cb40fce4ea56138e6a374` | `565dc502d78084ea4dcd8cf91104637a53ca0c80` | 1 | False | False | fetched | True | True | True |
| `yunionio/ocboot` | `b781237b81676ff5718525da798292e207124e01` | `a7ed6c2ee77582cedd079dc04ca7e9b1cff64ed4` | 1 | False | False | fetched | True | True | True |

The source pilot templates and contexts are not modified by this fetch. A refreshed pilot must be generated as a new version if these newly available diff candidates are admitted.
