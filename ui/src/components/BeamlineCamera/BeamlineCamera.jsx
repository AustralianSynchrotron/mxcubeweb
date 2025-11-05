import React, { useState, useRef, useEffect } from 'react';
import { Button, Dropdown, Card, Stack } from 'react-bootstrap';
import Draggable from 'react-draggable';
import { MdClose } from 'react-icons/md';
import styles from './beamlineCamera.module.css';
import pip from './picture_in_picture.svg';

function handleImageClick(url, width, height) {
  window.open(
    url,
    'webcam',
    `toolbar=0,location=0,menubar=0,addressbar=0,height=${height},width=${width}`,
    'popup',
  );
}

export default function BeamlineCamera(props) {
  const { cameraSetup } = props;
  const [showVideoModal, setShowVideoModal] = useState({});

  function handleShowVideoCard(key, value) {
    setShowVideoModal({ ...showVideoModal, [key]: value });
  }

  function renderVideo() {
    const DraggableElements = cameraSetup.components.map((camera, vIndex) => {
      if (showVideoModal[vIndex]) {
        return (
          <div
            key={`draggable-video_${camera.label}`}
            className="draggableHandle"
          >
            <Draggable defaultPosition={{ x: 200, y: 100 + 50 * vIndex }}>
              <Card className={styles.draggableHandle}>
                <Card.Header>
                  <Stack direction="horizontal" gap={3}>
                    <div className={styles.headerTitle}>{camera.label}</div>
                    <div className="p-2 ms-auto">
                      <Button
                        variant="outline-secondary"
                        onClick={() =>
                          handleImageClick(
                            camera.url,
                            camera.width,
                            camera.height
                          )
                        }
                        size="sm"
                      >
                        <img src={pip} alt="PIP Icon" />
                      </Button>
                    </div>
                    <div className="vr" />
                    <div>
                      <MdClose
                        color="red"
                        onClick={() => handleShowVideoCard(vIndex, false)}
                        size="1.5em"
                        className={styles.closeBtn}
                      />
                    </div>
                  </Stack>
                </Card.Header>
                <Card.Body>
                  {camera.format !== 'mp4' ? (
                    <CameraStreamImg
                      src={camera.url}
                      alt={camera.label}
                      width={camera.width}
                      height={camera.height}
                    />
                  ) : (
                    <video
                      src={camera.url}
                      alt={camera.label}
                      width={camera.width}
                      height={camera.height}
                    />
                  )}
                </Card.Body>
              </Card>
            </Draggable>
          </div>
        );
      }
      return null;
    });
    // Only use fragment if more than one child
    if (DraggableElements.filter(Boolean).length > 1) {
      return <>{DraggableElements}</>;
    }
    return DraggableElements.find(Boolean) || null;
  }

  if (!cameraSetup || cameraSetup.components.length <= 0) {
    return null;
  }

  return (
    <>
      <Dropdown
        title="Beamline Cameras"
        id="beamline-cameras-dropdown"
        variant="outline-secondary"
        autoClose="outside"
        key="beamline-cameras-dropdown"
      >
        <Dropdown.Toggle
          variant="outline-secondary"
          size="sm"
          className="mb-1"
          style={{ width: '150px' }}
        >
          Beamline Cameras
        </Dropdown.Toggle>
        <Dropdown.Menu>
          {cameraSetup.components.map((camera, cIndex) => [
            <Dropdown.Item
              key={`ddVideo_${camera.label}`}
              onClick={() => handleShowVideoCard(cIndex, true)}
            >
              {camera.label} <i className="fas fa-video" />
            </Dropdown.Item>,
            cameraSetup.components.length > cIndex + 1 && <Dropdown.Divider key={`divider_${camera.label}`} />,
          ])}
        </Dropdown.Menu>
      </Dropdown>
      {renderVideo()}
    </>
  );
}

// CameraStreamImg: <img> with auto-reconnect on error/abort and timeout
function CameraStreamImg({ src, alt, width, height }) {
  const [imgSrc, setImgSrc] = useState(`${src}?_t=${Date.now()}`);
  const imgRef = useRef();

  // Update src if the prop changes
  useEffect(() => {
    setImgSrc(`${src}?_t=${Date.now()}`);
  }, [src]);

  useEffect(() => {
    const img = imgRef.current;
    if (!img) {
      return undefined;
    }
    let timeoutId;
    const reload = () => setImgSrc(`${src}?_t=${Date.now()}`);
    const onLoad = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(reload, 10_000); // 10s timeout
    };
    img.addEventListener('error', reload);
    img.addEventListener('abort', reload);
    img.addEventListener('load', onLoad);
    timeoutId = setTimeout(reload, 10_000);
    return () => {
      img.removeEventListener('error', reload);
      img.removeEventListener('abort', reload);
      img.removeEventListener('load', onLoad);
      clearTimeout(timeoutId);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [imgSrc, src]);
  return (
    <img
      ref={imgRef}
      src={imgSrc}
      alt={alt}
      width={width}
      height={height}
      style={{ background: '#222' }}
    />
  );
}