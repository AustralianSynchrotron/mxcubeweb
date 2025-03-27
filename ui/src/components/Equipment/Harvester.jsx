import React from 'react';
import { Card, Button, Badge } from 'react-bootstrap';
import { contextMenu, Menu, Item, Separator } from 'react-contexify';
import { FcRefresh, FcUpload, FcCollect } from 'react-icons/fc';

import CopyToClipboard from '../CopyToClipboard/CopyToClipboard.jsx';
import ImageViewer from '../ImageViewer/ImageViewer.jsx';

import styles from './equipment.module.css';

const sampleStateBackground = (key) => {
  switch (key) {
    case 'ready_to_execute': {
      return 'success';
    }
    case 'harvested': {
      return 'info';
    }
    case 'needs_repositionning': {
      return 'warning';
    }
    case 'failed': {
      return 'danger';
    }
    default: {
      return 'info';
    }
  }
};

export default function Harvester(props) {
  function showContextMenu(event, id) {
    let position = {
      x: event.clientX,
      y: event.clientY,
    };
    if (props.inPopover) {
      position = {
        x: event.offsetX,
        y: event.offsetY,
      };
    }

    contextMenu.show({
      id,
      event,
      position,
    });
  }

  const harvestCrystal = (UUID) => {
    props.harvestCrystal(UUID);
  };

  const harvestAndLoadCrystal = (UUID) => {
    props.harvestAndLoadCrystal(UUID);
  };

  const renderCrystalMenu = (key) => (
    <Menu id={key}>
      <Item onClick={() => harvestCrystal(key)}>
        <span>
          harvest Crystal <FcCollect />
        </span>
      </Item>
      <Separator />
      <Item onClick={() => harvestAndLoadCrystal(key)}>
        <span>
          <FcCollect /> harvest & Load Sample <FcUpload />
        </span>
      </Item>
    </Menu>
  );

  const crystalUUID = props.contents.harvester_crystal_list;

  return (
    <Card>
      <Card.Header>
        <span style={{ marginLeft: '10px' }}>
          Number Of Available Pins : {props.contents.number_of_pins}
        </span>
      </Card.Header>
      <Card.Body>
        <div style={{ padding: '1em' }}>
          <Button
            variant="outline-secondary mb-2"
            onClick={props.handleRefresh}
          >
            <FcRefresh /> Refresh
          </Button>
          <div className={styles.ha_grid_container}>
            {crystalUUID
              ? crystalUUID.map((item) => (
                  <React.Fragment key={item.crystal_uuid}>
                    <div
                      key={item.crystal_uuid}
                      className={styles.ha_grid_item}
                      onContextMenu={(e) =>
                        showContextMenu(e, item.crystal_uuid)
                      }
                    >
                      <h6 className="text-center mt-1">
                        <Badge pill bg="light" style={{ color: 'brown' }}>
                          {item.name}
                        </Badge>
                      </h6>
                      <ImageViewer
                        galleryView={false}
                        imgUrl={item.img_url}
                        imageName={item.name}
                        imgAlt=""
                        imgTargetX={item.img_target_x}
                        imgTargetY={item.img_target_y}
                        drawTarget={false}
                      />
                      <div className={styles.crystal_uuid_caption}>
                        <div className="mt-1">
                          <Badge bg={sampleStateBackground(item.state)}>
                            {item.state ? item.state.replaceAll('_', ' ') : ''}
                          </Badge>
                        </div>
                        <div>
                          <span className="me-1">{item.crystal_uuid}</span>
                          <CopyToClipboard
                            text={item.crystal_uuid}
                            tittle="crystal uuid"
                            id={`copy_${item.crystal_uuid}`}
                          />
                        </div>
                      </div>
                    </div>
                    {renderCrystalMenu(item.crystal_uuid)}
                  </React.Fragment>
                ))
              : null}
          </div>
        </div>
      </Card.Body>
    </Card>
  );
}
