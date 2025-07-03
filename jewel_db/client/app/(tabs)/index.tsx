import { CameraView, CameraType, useCameraPermissions, CameraCapturedPicture } from 'expo-camera';
import { Image } from 'expo-image';
import { useRef, useState } from 'react';
import { Button, StyleSheet, Text, TouchableOpacity, View } from 'react-native';

export default function App() {
  const [facing, setFacing] = useState<CameraType>('front');
  const [picture, setPicture] = useState<CameraCapturedPicture>();
  const [permission, requestPermission] = useCameraPermissions();
  const cameraRef = useRef<CameraView>(null)
  if (!permission) {
    // Camera permissions are still loading.
    return <View />;
  }

  if (!permission.granted) {
    // Camera permissions are not granted yet.
    return (
      <View style={styles.container}>
        <Text style={styles.message}>We need your permission to show the camera</Text>
        <Button onPress={requestPermission} title="grant permission" />
      </View>
    );
  }

  const toggleCameraFacing = () => {
    setFacing(current => (current === 'back' ? 'front' : 'back'));
  }

  const takePicture = async() => {
    const picture = await cameraRef.current?.takePictureAsync({quality: 1, base64: true, exif: false})
    setPicture(picture)
  }

  const backToCamera = () => {
    setPicture(undefined)
  }

  return picture ? 
    <View style={styles.container}>
      <Image style={styles.preview} source={{uri: picture.base64}} />
        <View style={styles.backButtonContainer}>
          <TouchableOpacity style={styles.backButton} onPress={backToCamera}>
            <Text style={styles.text}>Back to camera NIKOOOLAAAAs</Text>
          </TouchableOpacity>
        </View>
    </View>
  : (
    <View style={styles.container}>
      <CameraView ref={cameraRef} style={styles.camera} facing={facing}>
        <View style={styles.buttonContainer}>
          <TouchableOpacity style={styles.button} onPress={takePicture}>
            <Text style={styles.text}>Take picture NIKOOOOO</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.button} onPress={toggleCameraFacing}>
            <Text style={styles.text}>Switch cameras</Text>
          </TouchableOpacity>
        </View>
      </CameraView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
  },
  message: {
    textAlign: 'center',
    paddingBottom: 10,
  },
  camera: {
    flex: 1,
  },
  buttonContainer: {
    flex: 1,
    flexDirection: 'row',
    backgroundColor: 'transparent',
    margin: 64,
  },
  backButtonContainer: {
    position: 'absolute',
    bottom: 16,
    flex: 1,
    backgroundColor: 'transparent',
    margin: 64,
  },
  button: {
    flex: 1,
    alignSelf: 'flex-end',
    alignItems: 'center',
  },
  text: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  backButton: {
    width: '100%',
    alignItems: 'center',
  },
  preview: {
    alignSelf: 'stretch',
    flex: 1,
    position: 'relative'
  }
});