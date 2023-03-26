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
  0.00001,
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

var stacy = null;

const loader = new THREE.GLTFLoader();
const stacy_loading = new Promise((resolve, reject) => {
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
        o.visible = false;
      }
      if (o.isBone) {
        bones[o.name] = o;
      }
    });

    // Set the models initial scale
    model.scale.set(7, 7, 7);
    model.position.y = -11;

    let axesHelper = new THREE.AxesHelper( 3 );
    model.add(axesHelper);

//    model.children[0].scale.set(1, 1, 1);

    scene.add(model);

    perspective.position.x = 10;
//    perspective.lookAt(model.children[0]);

    stacy = model.children[0];
//    stacy.scale.set(1, 1, 1);

    axesHelper = new THREE.AxesHelper( 2 );
    stacy.add(axesHelper);
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

let axesHelper = new THREE.AxesHelper( 8 );
scene.add(axesHelper);

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

const videoElement = document.getElementsByClassName('input', 'camera')[0];
const canvasElement = document.getElementsByClassName('output', 'camera')[0];
const canvasCtx = canvasElement.getContext('2d');

var hand_results;

const MEDIAPIPE_TO_THREE = {
  leftHandLandmarks: {
    0: 'mixamorigLeftHand',
    2: 'mixamorigLeftHandThumb2',
    3: 'mixamorigLeftHandThumb3',
    4: 'mixamorigLeftHandThumb4',
    5: 'mixamorigLeftHandIndex1',
    6: 'mixamorigLeftHandIndex2',
    7: 'mixamorigLeftHandIndex3',
    8: 'mixamorigLeftHandIndex4',
    9: 'mixamorigLeftHandMiddle1',
    10: 'mixamorigLeftHandMiddle2',
    11: 'mixamorigLeftHandMiddle3',
    12: 'mixamorigLeftHandMiddle4',
  },
  poseLandmarks: {
    12: 'mixamorigLeftShoulder',
    14: 'mixamorigLeftArm',
    16: 'mixamorigLeftForeArm',
  },
};

function make_connectors(){
  const connectors_summary = {
    central : [
      [11, 12],
      [23, 24],
    ],
    symetric: [
      [15, 19],
      [15, 17],
      [15, 21],
      [13, 15],
      [11, 13],
      [23, 11],
      [23, 25],
      [25, 27],
      [27, 29],
      [27, 31],
    ]
  };
  let connectors = [];
  for(const pair of connectors_summary.central){
    connectors.push([pair[0], pair[1]]);
  }
  for(const pair of connectors_summary.symetric){
    connectors.push([pair[0], pair[1]]);
    connectors.push([pair[0] + 1, pair[1] + 1]);
  }
  return connectors;
}

const connectors = make_connectors();

let cylinder_geometry = new THREE.CylinderGeometry(0.05, 0.05);
let cylinder_material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });

let spheres = [];
let cylinders = [];
let lines = [];
stacy_loading.then( () => {
  for(const connector_pair of connectors){
    let cylinder = new THREE.Mesh( cylinder_geometry, cylinder_material );
    cylinders[connector_pair.join(',')] = cylinder;
    model.add(cylinder);

    let line_geometry = new THREE.BufferGeometry();
    let line = new THREE.Line( line_geometry, cylinder_material);
    lines[connector_pair.join(',')] = line;
    model.add(line);
  }
});

let sphere_geometry = new THREE.SphereGeometry(0.02);
let sphere_material = new THREE.MeshBasicMaterial({ color: 0xff0000 });

const pr = pos => [ pos.x, pos.y, pos.z ];
var factor = {}, offset = {};
const to_three = pos => new THREE.Vector3( factor.x * pos.x + offset.x, -factor.y * pos.y + offset.y, -factor.z * pos.z + offset.z );
const avg = (p1, p2) => p1.clone().add(p2).divideScalar(2);
function set(reference, value){
  reference.set(value.x, value.y, value.z);
}

function rotatePointTo(parent, child, target){
//  console.log(`Rotating over ${pr(parent.position)} from ${pr(child.position)} to ${pr(target)}`)
  const PARENT_POS = new THREE.Vector3(0, 0, 0);

  let vpos = child.position.clone().sub(PARENT_POS);
  let vtarget = target.clone().sub(PARENT_POS);
  let cross = vpos.cross( vtarget );

  let sine_of_angle = cross.length() / (vpos.length() * vtarget.length());
  let angle = Math.asin(sine_of_angle);

  let vector = cross.normalize();

//  console.log(`Found axis (${[vector.x, vector.y, vector.z]}) and angle ${angle}`);
  child.quaternion.setFromAxisAngle( vector, angle );
}

const MAX_POINTS = 5;
var nb_points = 0;
var sum_offset = new THREE.Vector3(0, 0, 0);
var sum_factor = 0;

function onResults(results) {
  canvasCtx.save();
  canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
  if(results.segmentationMask)
    canvasCtx.drawImage(results.segmentationMask, 0, 0,
                      canvasElement.width, canvasElement.height);

  // Only overwrite existing pixels.
  canvasCtx.globalCompositeOperation = 'source-in';
  canvasCtx.fillStyle = '#00FF00';
  canvasCtx.fillRect(0, 0, canvasElement.width, canvasElement.height);

  // Only overwrite missing pixels.
  canvasCtx.globalCompositeOperation = 'destination-atop';
  canvasCtx.drawImage(
      results.image, 0, 0, canvasElement.width, canvasElement.height);

  canvasCtx.globalCompositeOperation = 'source-over';
  drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS,
                 {color: '#00FF00', lineWidth: 4});
  drawLandmarks(canvasCtx, results.poseLandmarks,
                {color: '#FF0000', lineWidth: 2});
  drawConnectors(canvasCtx, results.faceLandmarks, FACEMESH_TESSELATION,
                 {color: '#C0C0C070', lineWidth: 1});
  drawConnectors(canvasCtx, results.leftHandLandmarks, HAND_CONNECTIONS,
                 {color: '#CC0000', lineWidth: 5});
  drawLandmarks(canvasCtx, results.leftHandLandmarks,
                {color: '#00FF00', lineWidth: 2});
  drawConnectors(canvasCtx, results.rightHandLandmarks, HAND_CONNECTIONS,
                 {color: '#00CC00', lineWidth: 5});
  drawLandmarks(canvasCtx, results.rightHandLandmarks,
                {color: '#FF0000', lineWidth: 2});
  canvasCtx.restore();

  const hips = bones.mixamorigHips;
  const stacy = hips.parent;

  if(offset.x === undefined && results.poseLandmarks){
    const STACY_ARM_SIZE = bones.mixamorigLeftArm.position.length() * stacy.scale.x * stacy.parent.scale.x;
    const arm_begin = results.poseLandmarks[23], arm_end = results.poseLandmarks[24];
    const MEDIAPIPE_ARM_SIZE = (new THREE.Vector3( arm_end.x - arm_begin.x, arm_end.y - arm_begin.y, arm_end.z - arm_begin.z )).length();
    let factor_thistime = STACY_ARM_SIZE / MEDIAPIPE_ARM_SIZE;

    const left_foot = results.poseLandmarks[30], right_foot = results.poseLandmarks[31];
    const make_vector = coords => new THREE.Vector3( coords.x, coords.y, coords.z );
    const MEDIAPIPE_FLOOR = avg( make_vector(left_foot), make_vector(right_foot) );
    const STACY_FLOOR = model.worldToLocal( stacy.localToWorld( new THREE.Vector3(0, 0, 0) ) );
    let offset_thistime = MEDIAPIPE_FLOOR.sub(STACY_FLOOR);

    sum_offset.add( offset_thistime );
    sum_factor += factor_thistime;
    nb_points += 1;
    if(nb_points == MAX_POINTS){
      offset = sum_offset.divideScalar( nb_points );
      factor = sum_factor / nb_points;
      console.warn('Setting offset to ', offset, ' and factor to ', factor);
      factor = { x: factor, y: factor, z: factor };
    }
  }

  if(results.poseLandmarks){
    set(stacy.position,
      avg(
        to_three(results.poseLandmarks[23]),
        to_three(results.poseLandmarks[24])
      ).sub(
        hips.position.clone().multiply( stacy.scale ).applyQuaternion( stacy.quaternion )
      )
    );

    for(let pair of connectors){
      let first_endpoint = to_three( results.poseLandmarks[pair[0]] ),
        second_endpoint = to_three( results.poseLandmarks[pair[1]] );
      cylinders[pair.join(',')].scale.y = second_endpoint.clone().sub(first_endpoint).length();
      cylinders[pair.join(',')].lookAt( model.localToWorld( first_endpoint.clone() ) )
      cylinders[pair.join(',')].rotateX( Math.PI / 2 );
      set(cylinders[pair.join(',')].position, second_endpoint.clone().add(first_endpoint).divideScalar(2) );

      lines[pair.join(',')].geometry.setFromPoints( pair );
    }

    for(let batch of [ results.poseLandmarks ]){
      for(let point_index in batch){
        if(spheres[point_index] === undefined){
          spheres[point_index] = new THREE.Mesh(sphere_geometry, sphere_material);
          model.add(spheres[point_index]);
        }
        const new_coords = to_three(batch[point_index]);
        set( spheres[point_index].position, new_coords);
      }
    }
  }

  for(let [batch_name, batch] of Object.entries(MEDIAPIPE_TO_THREE)){
    if(results[batch_name]){
      for(let [index, boneName] of Object.entries(batch) ){
        let position_mediapipe = to_three(results[batch_name][index]);
/*
        let joint_three = bones[boneName];
        rotatePointTo(joint_three.parent, joint_three, joint_three.worldToLocal(position_mediapipe));
*/
        position_mediapipe = bones[boneName].worldToLocal( model.localToWorld( position_mediapipe ));
        set(bones[boneName].position, position_mediapipe.divideScalar(7));
      }
    }
  }
//  camera.stop();
}

const holistic = new Holistic({locateFile: (file) => {
  return `https://cdn.jsdelivr.net/npm/@mediapipe/holistic/${file}`;
}});
holistic.setOptions({
  modelComplexity: 1,
  smoothLandmarks: true,
  enableSegmentation: true,
  smoothSegmentation: true,
  refineFaceLandmarks: true,
  minDetectionConfidence: 0.5,
  minTrackingConfidence: 0.5
});
holistic.onResults(onResults);

const camera = new Camera(videoElement, {
  onFrame: async () => {
    await holistic.send({image: videoElement});
  },
  width: 640,
  height: 360
});
camera.start();
