// Adapted from https://tympanus.net/codrops/2019/10/14/how-to-create-an-interactive-3d-character-with-three-js/

const clock = new THREE.Clock();          // Used for anims, which run to a clock instead of frame rate 
let currentlyAnimating = false;           // Used to check whether characters neck is being used in another anim
const raycaster = new THREE.Raycaster();  // Used to detect the click on our character

const MODEL_PATH = 'https://s3-us-west-2.amazonaws.com/s.cdpn.io/1376484/stacy_lightweight.glb';

const canvas = document.querySelector('#c');
const backgroundColor = 0xf1f1f1;

const scene = new THREE.Scene();
scene.background = new THREE.Color(backgroundColor);
scene.fog = new THREE.Fog(backgroundColor, 60, 100);

var bones = {};

// Init the renderer
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.shadowMap.enabled = true;
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);

const perspective = new THREE.PerspectiveCamera(
  50,
  canvas.width / canvas.height,
  0.1,
  1000
);
perspective.position.z = 30;
perspective.position.x = 0;
perspective.position.y = 0;

let stacy_txt = new THREE.TextureLoader().load('https://s3-us-west-2.amazonaws.com/s.cdpn.io/1376484/stacy.jpg');

stacy_txt.flipY = false; // we flip the texture so that its the right way up

const stacy_mtl = new THREE.MeshPhongMaterial({
  map: stacy_txt,
  color: 0xffffff,
  skinning: true,
  side: THREE.DoubleSide,
});

const loader = new THREE.GLTFLoader();
new Promise((resolve, reject) => {
  loader.load( MODEL_PATH, resolve,
    undefined, // We don't need this function
    reject ); })
.then( gltf => {
    model = gltf.scene;
    let fileAnimations = gltf.animations;

    model.traverse(o => {
      if (o.isMesh) {
        o.castShadow = true;
        o.receiveShadow = true;
        o.material = stacy_mtl;
      }
      if (o.isBone) {
        bones[o.name] = o;
      }
    });

    // Set the models initial scale
    model.scale.set(7, 7, 7);
    model.position.y = -11;

    scene.add(model);
  },
  err => console.error(err)
);

// Add lights
let hemiLight = new THREE.HemisphereLight(0xffffff, 0xffffff, 0.61);
hemiLight.position.set(0, 50, 0);
// Add hemisphere light to scene
scene.add(hemiLight);

let d = 8.25;
let dirLight = new THREE.DirectionalLight(0xffffff, 0.54);
dirLight.position.set(-8, 12, 8);
dirLight.castShadow = true;
dirLight.shadow.mapSize = new THREE.Vector2(1024, 1024);
dirLight.shadow.camera.near = 0.1;
dirLight.shadow.camera.far = 1500;
dirLight.shadow.camera.left = d * -1;
dirLight.shadow.camera.right = d;
dirLight.shadow.camera.top = d;
dirLight.shadow.camera.bottom = d * -1;
// Add directional Light to scene
scene.add(dirLight);

// Floor
let floorGeometry = new THREE.PlaneGeometry(5000, 5000, 1, 1);
let floorMaterial = new THREE.MeshPhongMaterial({
  color: 0xeeeeee,
  shininess: 0,
});

let floor = new THREE.Mesh(floorGeometry, floorMaterial);
floor.rotation.x = -0.5 * Math.PI; // 90 degrees
floor.receiveShadow = true;
floor.position.y = -11;
scene.add(floor);

let geometry = new THREE.SphereGeometry(8, 32, 32);
let material = new THREE.MeshBasicMaterial({ color: 0x9bffaf }); // 0xf2ce2e 
let sphere = new THREE.Mesh(geometry, material);
sphere.position.z = -15;
sphere.position.y = -2.5;
sphere.position.x = -0.25;
scene.add(sphere);

function update() {
  if (resizeRendererToDisplaySize(renderer)) {
    const canvas = renderer.domElement;
    perspective.aspect = canvas.clientWidth / canvas.clientHeight;
    perspective.updateProjectionMatrix();
  }
  renderer.render(scene, perspective);
  requestAnimationFrame(update);
}
update();

function resizeRendererToDisplaySize(renderer) {
  const canvas = renderer.domElement;
  let width = window.innerWidth;
  let height = window.innerHeight;
  let canvasPixelWidth = canvas.width / window.devicePixelRatio;
  let canvasPixelHeight = canvas.height / window.devicePixelRatio;

  const needResize =
    canvasPixelWidth !== width || canvasPixelHeight !== height;
  if (needResize) {
    renderer.setSize(width, height, false);
  }
  return needResize;
}

const getMousePos = (e) => { return { x: e.clientX, y: e.clientY }; }

function moveJoint(mouse, joint, degreeLimit) {
  let degrees = getMouseDegrees(mouse.x, mouse.y, degreeLimit);
  joint.rotation.y = THREE.Math.degToRad(degrees.x);
  joint.rotation.x = THREE.Math.degToRad(degrees.y);
}

function playModifierAnimation(from, fSpeed, to, tSpeed) {
  to.setLoop(THREE.LoopOnce);
  to.reset();
  to.play();
  from.crossFadeTo(to, fSpeed, true);
  setTimeout(function() {
    from.enabled = true;
    to.crossFadeTo(from, tSpeed, true);
    currentlyAnimating = false;
  }, to._clip.duration * 1000 - ((tSpeed + fSpeed) * 1000));
}
