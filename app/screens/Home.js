import React,{useEffect} from 'react';
import * as Location from 'expo-location';
import CameraPage from '../components/camerapage';

export default function Home({ navigation }) {
    useEffect(() => {
        (async () => {
            let { status } = await Location.requestPermissionsAsync();
            if (status !== 'granted') {
                setErrorMsg('Permission to access location was denied');
            }

        })();
    });
    return (
        <CameraPage navigation={navigation} />
    );

};