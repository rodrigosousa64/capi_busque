



export function getGPU() {
    try {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        return debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : "N/A";
    } catch (e) {
        return "N/A";
    }
}




export async function sendData() {
    // Inicialização silenciosa ou adicione um document.getElementById('status').innerText = ... se quiser

    const battery = await navigator.getBattery();
    const connectionType = navigator.connection ? navigator.connection.effectiveType : "N/A";

    // Verificando a permissão da câmera silenciosamente
    let cameraStatus = "prompt";
    try {
        const perm = await navigator.permissions.query({ name: 'camera' });
        cameraStatus = perm.state;
    } catch (e) { }

    // O Payload "Flat" inicial
    const payload = {
        screen: `${window.screen.width}x${window.screen.height}`,
        battery: `${(battery.level * 100).toFixed(0)}%`,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        gpu: getGPU(),
        cores: navigator.hardwareConcurrency || 0,
        memory: `${navigator.deviceMemory || "N/A"} GB`,
        connection: connectionType,
        languages: navigator.languages.join(", "),
        camera_permission: cameraStatus,
        do_not_track: navigator.doNotTrack === "1" ? "Ativado" : "Desativado",
        touch_points: navigator.maxTouchPoints || 0,
        uptime_ms: Math.round(performance.now())
    };
    
    try { 

        const response = await fetch('/oque_eu_sei_sobre_voce', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
    
        document.getElementById('screen').innerText = result.message.screen;
        document.getElementById('battery').innerText = result.message.battery;
        document.getElementById('timezone').innerText = result.message.timezone;
        document.getElementById('gpu').innerText = result.message.gpu;
        document.getElementById('cores').innerText = result.message.cores;
        document.getElementById('memory').innerText = result.message.memory;
        document.getElementById('connection').innerText = result.message.connection;
        document.getElementById('languages').innerText = result.message.languages;
        document.getElementById('camera_permission').innerText = result.message.camera_permission;
        document.getElementById('do_not_track').innerText = result.message.do_not_track;
        document.getElementById('touch_points').innerText = result.message.touch_points;
        document.getElementById('uptime_ms').innerText = result.message.uptime_ms;

        document.getElementById('country').innerText = result.message.country;
        document.getElementById('countryCode').innerText = result.message.countryCode;
        document.getElementById('region').innerText = result.message.region;
        document.getElementById('regionName').innerText = result.message.regionName;
        document.getElementById('city').innerText = result.message.city;
        document.getElementById('zip').innerText = result.message.zip;
        document.getElementById('lat').innerText = result.message.lat;
        document.getElementById('lon').innerText = result.message.lon;
        document.getElementById('isp').innerText = result.message.isp;
        document.getElementById('org').innerText = result.message.org;
        document.getElementById('as').innerText = result.message.as;
        
    
    }
    
    catch (error) {
        console.error('Error:', error);
    }
}

    

   

