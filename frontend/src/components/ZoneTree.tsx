import React from 'react';
import { 
  List, 
  ListItem, 
  ListItemText, 
  ListItemIcon, 
  Collapse, 
  IconButton,
  ListItemSecondaryAction,
  Divider,
  Menu,
  MenuItem,
  Typography,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  FolderOutlined as FolderIcon,
  DevicesOutlined as ServerIcon,
  MoreVert as MoreIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { Zone, Environment, Server } from '../models/types';

interface ZoneTreeProps {
  zones: Zone[];
  selectedZone: Zone | null;
  selectedEnvironment: Environment | null;
  onSelectZone: (zoneName: string) => void;
  onSelectEnvironment: (envName: string) => void;
  onAddZone: () => void;
  onEditZone: (zone: Zone) => void;
  onDeleteZone: (zoneName: string) => void;
  onAddEnvironment: (zoneName: string) => void;
  onEditEnvironment: (zoneName: string, environment: Environment) => void;
  onDeleteEnvironment: (zoneName: string, envName: string) => void;
  onAddServer: (zoneName: string, envName: string) => void;
}

const ZoneTree: React.FC<ZoneTreeProps> = ({
  zones,
  selectedZone,
  selectedEnvironment,
  onSelectZone,
  onSelectEnvironment,
  onAddZone,
  onEditZone,
  onDeleteZone,
  onAddEnvironment,
  onEditEnvironment,
  onDeleteEnvironment,
  onAddServer,
}) => {
  // Состояние для раскрытых элементов
  const [expandedZones, setExpandedZones] = React.useState<{ [key: string]: boolean }>({});
  const [expandedEnvs, setExpandedEnvs] = React.useState<{ [key: string]: boolean }>({});

  // Состояние для меню
  const [zoneMenuAnchor, setZoneMenuAnchor] = React.useState<null | HTMLElement>(null);
  const [environmentMenuAnchor, setEnvironmentMenuAnchor] = React.useState<null | HTMLElement>(null);
  const [selectedMenuZone, setSelectedMenuZone] = React.useState<Zone | null>(null);
  const [selectedMenuEnv, setSelectedMenuEnv] = React.useState<Environment | null>(null);

  // Обработчики переключения раскрытия
  const handleToggleZone = (zoneName: string) => {
    setExpandedZones(prev => ({
      ...prev,
      [zoneName]: !prev[zoneName]
    }));
  };

  const handleToggleEnv = (envKey: string) => {
    setExpandedEnvs(prev => ({
      ...prev,
      [envKey]: !prev[envKey]
    }));
  };

  // Обработчики меню для зон
  const handleZoneMenuOpen = (event: React.MouseEvent<HTMLElement>, zone: Zone) => {
    event.stopPropagation();
    setZoneMenuAnchor(event.currentTarget);
    setSelectedMenuZone(zone);
  };

  const handleZoneMenuClose = () => {
    setZoneMenuAnchor(null);
    setSelectedMenuZone(null);
  };

  // Обработчики меню для окружений
  const handleEnvironmentMenuOpen = (event: React.MouseEvent<HTMLElement>, zone: Zone, env: Environment) => {
    event.stopPropagation();
    setEnvironmentMenuAnchor(event.currentTarget);
    setSelectedMenuZone(zone);
    setSelectedMenuEnv(env);
  };

  const handleEnvironmentMenuClose = () => {
    setEnvironmentMenuAnchor(null);
    setSelectedMenuZone(null);
    setSelectedMenuEnv(null);
  };

  // Обработчики действий меню
  const handleEditZone = () => {
    if (selectedMenuZone) {
      onEditZone(selectedMenuZone);
    }
    handleZoneMenuClose();
  };

  const handleDeleteZone = () => {
    if (selectedMenuZone) {
      onDeleteZone(selectedMenuZone.name);
    }
    handleZoneMenuClose();
  };

  const handleAddEnvironment = () => {
    if (selectedMenuZone) {
      onAddEnvironment(selectedMenuZone.name);
    }
    handleZoneMenuClose();
  };

  const handleEditEnvironment = () => {
    if (selectedMenuZone && selectedMenuEnv) {
      onEditEnvironment(selectedMenuZone.name, selectedMenuEnv);
    }
    handleEnvironmentMenuClose();
  };

  const handleDeleteEnvironment = () => {
    if (selectedMenuZone && selectedMenuEnv) {
      onDeleteEnvironment(selectedMenuZone.name, selectedMenuEnv.name);
    }
    handleEnvironmentMenuClose();
  };

  const handleAddServer = () => {
    if (selectedMenuZone && selectedMenuEnv) {
      onAddServer(selectedMenuZone.name, selectedMenuEnv.name);
    }
    handleEnvironmentMenuClose();
  };

  return (
    <>
      <List
        component="nav"
        aria-labelledby="zones-list"
        sx={{ width: '100%', bgcolor: 'background.paper' }}
      >
        <ListItem
          sx={{
            bgcolor: 'background.default',
            position: 'sticky',
            top: 0,
            zIndex: 1,
          }}
        >
          <ListItemText
            primary={
              <Typography variant="subtitle1" fontWeight="bold">
                Зоны и окружения
              </Typography>
            }
          />
          <IconButton edge="end" aria-label="add-zone" onClick={onAddZone}>
            <AddIcon />
          </IconButton>
        </ListItem>
        
        <Divider />
        
        {zones.length === 0 ? (
          <ListItem>
            <ListItemText primary="Нет доступных зон" />
          </ListItem>
        ) : (
          zones.map((zone) => (
            <React.Fragment key={zone.name}>
              <ListItem
                component="div"
                disablePadding
                onClick={() => {
                  onSelectZone(zone.name);
                  handleToggleZone(zone.name);
                }}
                sx={{ 
                  bgcolor: selectedZone?.name === zone.name && !selectedEnvironment ? 'action.selected' : 'inherit'
                }}
              >
                <ListItemIcon>
                  <FolderIcon />
                </ListItemIcon>
                <ListItemText primary={zone.name} />
                {expandedZones[zone.name] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                <ListItemSecondaryAction>
                  <IconButton edge="end" aria-label="options" onClick={(e: React.MouseEvent<HTMLElement>) => handleZoneMenuOpen(e, zone)}>
                    <MoreIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
              
              <Collapse in={expandedZones[zone.name]} timeout="auto" unmountOnExit>
                <List component="div" disablePadding>
                  {zone.environments.length === 0 ? (
                    <ListItem sx={{ pl: 4 }}>
                      <ListItemText primary="Нет окружений" secondary="Нажмите + чтобы добавить" />
                    </ListItem>
                  ) : (
                    zone.environments.map((env) => (
                      <React.Fragment key={`${zone.name}-${env.name}`}>
                        <ListItem
                          component="div"
                          disablePadding
                          sx={{ 
                            pl: 4,
                            bgcolor: selectedZone?.name === zone.name && selectedEnvironment?.name === env.name ? 'action.selected' : 'inherit'
                          }}
                          onClick={() => {
                            onSelectZone(zone.name);
                            onSelectEnvironment(env.name);
                            handleToggleEnv(`${zone.name}-${env.name}`);
                          }}
                        >
                          <ListItemIcon>
                            <ServerIcon />
                          </ListItemIcon>
                          <ListItemText primary={env.name} />
                          {expandedEnvs[`${zone.name}-${env.name}`] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                          <ListItemSecondaryAction>
                            <IconButton
                              edge="end"
                              aria-label="options"
                              onClick={(e: React.MouseEvent<HTMLElement>) => handleEnvironmentMenuOpen(e, zone, env)}
                            >
                              <MoreIcon />
                            </IconButton>
                          </ListItemSecondaryAction>
                        </ListItem>
                        
                        <Collapse in={expandedEnvs[`${zone.name}-${env.name}`]} timeout="auto" unmountOnExit>
                          <List component="div" disablePadding>
                            {env.servers.length === 0 ? (
                              <ListItem sx={{ pl: 8 }}>
                                <ListItemText primary="Нет серверов" secondary="Нажмите + чтобы добавить" />
                              </ListItem>
                            ) : (
                              env.servers.map((server) => (
                                <ListItem key={server.fqdn} sx={{ pl: 8 }}>
                                  <ListItemIcon>
                                    <ServerIcon />
                                  </ListItemIcon>
                                  <ListItemText
                                    primary={server.fqdn}
                                    secondary={`${server.ip} - ${server.status}`}
                                  />
                                </ListItem>
                              ))
                            )}
                          </List>
                        </Collapse>
                      </React.Fragment>
                    ))
                  )}
                </List>
              </Collapse>
            </React.Fragment>
          ))
        )}
      </List>
      
      {/* Меню для зон */}
      <Menu
        anchorEl={zoneMenuAnchor}
        open={Boolean(zoneMenuAnchor)}
        onClose={handleZoneMenuClose}
      >
        <MenuItem onClick={handleEditZone}>Редактировать зону</MenuItem>
        <MenuItem onClick={handleDeleteZone}>Удалить зону</MenuItem>
        <MenuItem onClick={handleAddEnvironment}>Добавить окружение</MenuItem>
      </Menu>
      
      {/* Меню для окружений */}
      <Menu
        anchorEl={environmentMenuAnchor}
        open={Boolean(environmentMenuAnchor)}
        onClose={handleEnvironmentMenuClose}
      >
        <MenuItem onClick={handleEditEnvironment}>Редактировать окружение</MenuItem>
        <MenuItem onClick={handleDeleteEnvironment}>Удалить окружение</MenuItem>
        <MenuItem onClick={handleAddServer}>Добавить сервер</MenuItem>
      </Menu>
    </>
  );
};

export default ZoneTree; 