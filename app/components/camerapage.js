import React, { useState, useEffect } from 'react';
import { Text, View, TouchableOpacity, TouchableWithoutFeedback } from 'react-native';
import { Camera } from 'expo-camera';
import styles from '../constants/styles';
import Toolbar from '../components/toolbar';
import { Col, Row, Grid } from "react-native-easy-grid";



export default function CameraPage({navigation}) {
    const [hasPermission, setHasPermission] = useState(null);
    const [cameraRef, setCameraRef] = useState(null)
    const [Image, setImage] = useState(null)
    
    const [type, setType] = useState(Camera.Constants.Type.back); useEffect(() => {
        (async () => {
            const { status } = await Camera.requestPermissionsAsync();
            setHasPermission(status === 'granted');
        })();
    }, []); if (hasPermission === null) {
        return <View />;
    }
    if (hasPermission === false) {
        return <Text>No access to camera</Text>;
    }
    return (
        <View style={{ flex: 1 }}>
            <Camera style={{ flex: 1 }} type={type} ref={ref => {
                setCameraRef(ref);
            }}>
                <View
                    style={{
                        flex: 1,
                        backgroundColor: 'transparent',
                        flexDirection: 'row',
                    }}>
                    <Toolbar cameraRef={cameraRef} navigation={navigation}/>
                </View>
            </Camera>
        </View>
    );
}
