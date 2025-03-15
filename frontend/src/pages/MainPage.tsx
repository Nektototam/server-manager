import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useData } from '../context/DataContext';
import { Zone, Environment, Server } from '../models/types';
import ZoneTree from '../components/ZoneTree';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Container,
  Grid,
  Paper,
  Box,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
  MenuItem,
  Select,
  SelectChangeEvent,
  FormControl,
  InputLabel,
  Divider,
  IconButton,
  Card,
  CardContent,
  CardHeader,
  Alert,
  Snackbar,
  FormHelperText,
} from '@mui/material';
import {
  ExitToApp as LogoutIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
} from '@mui/icons-material';
import { Formik, Form, Field, FormikHelpers } from 'formik';
import * as Yup from 'yup';

// Схемы валидации
const ZoneSchema = Yup.object().shape({
  name: Yup.string().required('Обязательное поле'),
});

const EnvironmentSchema = Yup.object().shape({
  name: Yup.string().required('Обязательное поле'),
});

const ServerSchema = Yup.object().shape({
  fqdn: Yup.string().required('Обязательное поле'),
  ip: Yup.string().required('Обязательное поле').matches(/^(\d{1,3}\.){3}\d{1,3}$/, 'Неверный формат IP'),
  status: Yup.string().required('Обязательное поле'),
  server_type: Yup.string().required('Обязательное поле'),
});

const MainPage: React.FC = () => {
  const { logout, user } = useAuth();
  const { 
    zones, 
    selectedZone,
    selectedEnvironment,
    loading: dataLoading, 
    error: dataError,
    fetchZones,
    selectZone,
    selectEnvironment,
    createZone,
    updateZone,
    deleteZone,
    createEnvironment,
    updateEnvironment,
    deleteEnvironment,
    addServer,
    updateServer,
    deleteServer,
  } = useData();
  const navigate = useNavigate();
  
  // Состояние для диалогов
  const [zoneDialogOpen, setZoneDialogOpen] = useState(false);
  const [environmentDialogOpen, setEnvironmentDialogOpen] = useState(false);
  const [serverDialogOpen, setServerDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState<'create' | 'edit'>('create');
  const [deleteTarget, setDeleteTarget] = useState<{ type: 'zone' | 'environment' | 'server'; name: string; zoneName?: string; envName?: string; }>({ type: 'zone', name: '' });
  
  // Состояние для уведомлений
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' | 'info' | 'warning' }>({
    open: false,
    message: '',
    severity: 'info',
  });
  
  // Состояние для редактирования
  const [editingZone, setEditingZone] = useState<Zone | null>(null);
  const [editingEnvironment, setEditingEnvironment] = useState<Environment | null>(null);
  const [editingServer, setEditingServer] = useState<Server | null>(null);
  const [parentZoneName, setParentZoneName] = useState<string>('');
  const [parentEnvName, setParentEnvName] = useState<string>('');

  // Обработчик выхода
  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Обработчики для зон
  const handleAddZone = () => {
    setDialogMode('create');
    setEditingZone({ name: '', type: 'zone', environments: [] });
    setZoneDialogOpen(true);
  };

  const handleEditZone = (zone: Zone) => {
    setDialogMode('edit');
    setEditingZone(zone);
    setZoneDialogOpen(true);
  };

  const handleDeleteZone = (zoneName: string) => {
    setDeleteTarget({ type: 'zone', name: zoneName });
    setDeleteDialogOpen(true);
  };

  // Обработчики для окружений
  const handleAddEnvironment = (zoneName: string) => {
    setDialogMode('create');
    setEditingEnvironment({ name: '', servers: [] });
    setParentZoneName(zoneName);
    setEnvironmentDialogOpen(true);
  };

  const handleEditEnvironment = (zoneName: string, environment: Environment) => {
    setDialogMode('edit');
    setEditingEnvironment(environment);
    setParentZoneName(zoneName);
    setEnvironmentDialogOpen(true);
  };

  const handleDeleteEnvironment = (zoneName: string, envName: string) => {
    setDeleteTarget({ type: 'environment', name: envName, zoneName });
    setDeleteDialogOpen(true);
  };

  // Обработчики для серверов
  const handleAddServer = (zoneName: string, envName: string) => {
    setDialogMode('create');
    setEditingServer({ fqdn: '', ip: '', status: 'available', server_type: '' });
    setParentZoneName(zoneName);
    setParentEnvName(envName);
    setServerDialogOpen(true);
  };

  // Обработчики подтверждения диалогов
  const handleZoneSubmit = async (values: { name: string }, { setSubmitting }: FormikHelpers<{ name: string }>) => {
    try {
      if (dialogMode === 'create') {
        await createZone({
          name: values.name,
          type: 'zone',
          environments: [],
        });
        setSnackbar({ open: true, message: 'Зона успешно создана', severity: 'success' });
      } else if (dialogMode === 'edit' && editingZone) {
        await updateZone({
          ...editingZone,
          name: values.name,
        });
        setSnackbar({ open: true, message: 'Зона успешно обновлена', severity: 'success' });
      }
      setZoneDialogOpen(false);
    } catch (error) {
      console.error('Ошибка при работе с зоной:', error);
      setSnackbar({ open: true, message: 'Ошибка при сохранении зоны', severity: 'error' });
    } finally {
      setSubmitting(false);
    }
  };

  const handleEnvironmentSubmit = async (values: { name: string }, { setSubmitting }: FormikHelpers<{ name: string }>) => {
    try {
      if (dialogMode === 'create') {
        await createEnvironment(parentZoneName, {
          name: values.name,
          servers: [],
        });
        setSnackbar({ open: true, message: 'Окружение успешно создано', severity: 'success' });
      } else if (dialogMode === 'edit' && editingEnvironment) {
        await updateEnvironment(parentZoneName, editingEnvironment.name, {
          ...editingEnvironment,
          name: values.name,
        });
        setSnackbar({ open: true, message: 'Окружение успешно обновлено', severity: 'success' });
      }
      setEnvironmentDialogOpen(false);
    } catch (error) {
      console.error('Ошибка при работе с окружением:', error);
      setSnackbar({ open: true, message: 'Ошибка при сохранении окружения', severity: 'error' });
    } finally {
      setSubmitting(false);
    }
  };

  const handleServerSubmit = async (values: Server, { setSubmitting }: FormikHelpers<Server>) => {
    try {
      if (dialogMode === 'create') {
        await addServer(parentZoneName, parentEnvName, values);
        setSnackbar({ open: true, message: 'Сервер успешно добавлен', severity: 'success' });
      } else if (dialogMode === 'edit' && editingServer) {
        await updateServer(parentZoneName, parentEnvName, editingServer.fqdn, values);
        setSnackbar({ open: true, message: 'Сервер успешно обновлен', severity: 'success' });
      }
      setServerDialogOpen(false);
    } catch (error) {
      console.error('Ошибка при работе с сервером:', error);
      setSnackbar({ open: true, message: 'Ошибка при сохранении сервера', severity: 'error' });
    } finally {
      setSubmitting(false);
    }
  };

  // Подтверждение удаления
  const handleDeleteConfirm = async () => {
    try {
      if (deleteTarget.type === 'zone') {
        await deleteZone(deleteTarget.name);
        setSnackbar({ open: true, message: 'Зона успешно удалена', severity: 'success' });
      } else if (deleteTarget.type === 'environment' && deleteTarget.zoneName) {
        await deleteEnvironment(deleteTarget.zoneName, deleteTarget.name);
        setSnackbar({ open: true, message: 'Окружение успешно удалено', severity: 'success' });
      } else if (deleteTarget.type === 'server' && deleteTarget.zoneName && deleteTarget.envName) {
        await deleteServer(deleteTarget.zoneName, deleteTarget.envName, deleteTarget.name);
        setSnackbar({ open: true, message: 'Сервер успешно удален', severity: 'success' });
      }
    } catch (error) {
      console.error('Ошибка при удалении:', error);
      setSnackbar({ open: true, message: `Ошибка при удалении ${deleteTarget.type}`, severity: 'error' });
    } finally {
      setDeleteDialogOpen(false);
    }
  };

  // Отображение основной информации
  const renderContent = () => {
    if (dataLoading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
          <CircularProgress />
        </Box>
      );
    }

    if (dataError) {
      return (
        <Box sx={{ p: 3 }}>
          <Alert severity="error">{dataError}</Alert>
        </Box>
      );
    }

    if (selectedZone) {
      return (
        <Box sx={{ p: 3 }}>
          <Card>
            <CardHeader
              title={selectedZone.name}
              subheader={`Тип: ${selectedZone.type}`}
              action={
                <Box>
                  <IconButton onClick={() => handleEditZone(selectedZone)}>
                    <EditIcon />
                  </IconButton>
                  <IconButton onClick={() => handleDeleteZone(selectedZone.name)}>
                    <DeleteIcon />
                  </IconButton>
                  <IconButton onClick={() => handleAddEnvironment(selectedZone.name)}>
                    <AddIcon />
                  </IconButton>
                </Box>
              }
            />
            <Divider />
            <CardContent>
              {selectedEnvironment ? (
                <>
                  <Typography variant="h6" gutterBottom>
                    Окружение: {selectedEnvironment.name}
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Button
                      variant="outlined"
                      startIcon={<EditIcon />}
                      onClick={() => handleEditEnvironment(selectedZone.name, selectedEnvironment)}
                      sx={{ mr: 1 }}
                    >
                      Редактировать
                    </Button>
                    <Button
                      variant="outlined"
                      color="error"
                      startIcon={<DeleteIcon />}
                      onClick={() => handleDeleteEnvironment(selectedZone.name, selectedEnvironment.name)}
                      sx={{ mr: 1 }}
                    >
                      Удалить
                    </Button>
                    <Button
                      variant="outlined"
                      color="primary"
                      startIcon={<AddIcon />}
                      onClick={() => handleAddServer(selectedZone.name, selectedEnvironment.name)}
                    >
                      Добавить сервер
                    </Button>
                  </Box>
                  <Divider sx={{ mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Серверы ({selectedEnvironment.servers.length})
                  </Typography>
                  {selectedEnvironment.servers.length === 0 ? (
                    <Typography>Нет серверов в этом окружении</Typography>
                  ) : (
                    <Grid container spacing={2}>
                      {selectedEnvironment.servers.map((server) => (
                        <Grid item xs={12} md={6} lg={4} key={server.fqdn}>
                          <Card variant="outlined">
                            <CardContent>
                              <Typography variant="h6">{server.fqdn}</Typography>
                              <Typography variant="body2" color="textSecondary">
                                IP: {server.ip}
                              </Typography>
                              <Typography variant="body2" color="textSecondary">
                                Статус: {server.status}
                              </Typography>
                              <Typography variant="body2" color="textSecondary">
                                Тип: {server.server_type}
                              </Typography>
                            </CardContent>
                          </Card>
                        </Grid>
                      ))}
                    </Grid>
                  )}
                </>
              ) : (
                <>
                  <Typography variant="h6" gutterBottom>
                    Окружения ({selectedZone.environments.length})
                  </Typography>
                  {selectedZone.environments.length === 0 ? (
                    <Typography>Нет окружений в этой зоне</Typography>
                  ) : (
                    <Grid container spacing={2}>
                      {selectedZone.environments.map((env) => (
                        <Grid item xs={12} md={6} lg={4} key={env.name}>
                          <Card variant="outlined">
                            <CardContent>
                              <Typography variant="h6">{env.name}</Typography>
                              <Typography variant="body2" color="textSecondary">
                                Количество серверов: {env.servers.length}
                              </Typography>
                              <Box sx={{ mt: 1 }}>
                                <Button 
                                  size="small" 
                                  onClick={() => {
                                    selectZone(selectedZone.name);
                                    selectEnvironment(env.name);
                                  }}
                                >
                                  Показать серверы
                                </Button>
                              </Box>
                            </CardContent>
                          </Card>
                        </Grid>
                      ))}
                    </Grid>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </Box>
      );
    }

    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Добро пожаловать в систему управления серверами
        </Typography>
        <Typography paragraph>
          Выберите зону из списка слева или создайте новую зону, чтобы начать работу.
        </Typography>
      </Box>
    );
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Управление серверными ресурсами
          </Typography>
          {user && (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography variant="body2" sx={{ mr: 2 }}>
                {user.username}
              </Typography>
              <Button color="inherit" onClick={handleLogout} startIcon={<LogoutIcon />}>
                Выйти
              </Button>
            </Box>
          )}
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ flexGrow: 1, display: 'flex', mt: 2, mb: 2 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={3}>
            <Paper sx={{ height: '100%', minHeight: '500px', overflow: 'auto' }}>
              <ZoneTree
                zones={zones}
                selectedZone={selectedZone}
                selectedEnvironment={selectedEnvironment}
                onSelectZone={selectZone}
                onSelectEnvironment={selectEnvironment}
                onAddZone={handleAddZone}
                onEditZone={handleEditZone}
                onDeleteZone={handleDeleteZone}
                onAddEnvironment={handleAddEnvironment}
                onEditEnvironment={handleEditEnvironment}
                onDeleteEnvironment={handleDeleteEnvironment}
                onAddServer={handleAddServer}
              />
            </Paper>
          </Grid>
          <Grid item xs={12} md={9}>
            <Paper sx={{ height: '100%', minHeight: '500px' }}>
              {renderContent()}
            </Paper>
          </Grid>
        </Grid>
      </Container>

      {/* Диалог для зоны */}
      <Dialog open={zoneDialogOpen} onClose={() => setZoneDialogOpen(false)}>
        <DialogTitle>{dialogMode === 'create' ? 'Создать зону' : 'Редактировать зону'}</DialogTitle>
        <Formik
          initialValues={{ name: editingZone?.name || '' }}
          validationSchema={ZoneSchema}
          onSubmit={handleZoneSubmit}
        >
          {({ values, handleChange, handleBlur, errors, touched, isSubmitting }: {
            values: { name: string };
            handleChange: React.ChangeEventHandler;
            handleBlur: React.FocusEventHandler;
            errors: { name?: string };
            touched: { name?: boolean };
            isSubmitting: boolean;
          }) => (
            <Form>
              <DialogContent>
                <TextField
                  fullWidth
                  id="name"
                  name="name"
                  label="Имя зоны"
                  value={values.name}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={touched.name && Boolean(errors.name)}
                  helperText={touched.name && errors.name}
                  margin="normal"
                />
              </DialogContent>
              <DialogActions>
                <Button onClick={() => setZoneDialogOpen(false)}>Отмена</Button>
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? <CircularProgress size={24} /> : 'Сохранить'}
                </Button>
              </DialogActions>
            </Form>
          )}
        </Formik>
      </Dialog>

      {/* Диалог для окружения */}
      <Dialog open={environmentDialogOpen} onClose={() => setEnvironmentDialogOpen(false)}>
        <DialogTitle>{dialogMode === 'create' ? 'Создать окружение' : 'Редактировать окружение'}</DialogTitle>
        <Formik
          initialValues={{ name: editingEnvironment?.name || '' }}
          validationSchema={EnvironmentSchema}
          onSubmit={handleEnvironmentSubmit}
        >
          {({ values, handleChange, handleBlur, errors, touched, isSubmitting }: {
            values: { name: string };
            handleChange: React.ChangeEventHandler;
            handleBlur: React.FocusEventHandler;
            errors: { name?: string };
            touched: { name?: boolean };
            isSubmitting: boolean;
          }) => (
            <Form>
              <DialogContent>
                <TextField
                  fullWidth
                  id="name"
                  name="name"
                  label="Имя окружения"
                  value={values.name}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={touched.name && Boolean(errors.name)}
                  helperText={touched.name && errors.name}
                  margin="normal"
                />
              </DialogContent>
              <DialogActions>
                <Button onClick={() => setEnvironmentDialogOpen(false)}>Отмена</Button>
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? <CircularProgress size={24} /> : 'Сохранить'}
                </Button>
              </DialogActions>
            </Form>
          )}
        </Formik>
      </Dialog>

      {/* Диалог для сервера */}
      <Dialog open={serverDialogOpen} onClose={() => setServerDialogOpen(false)}>
        <DialogTitle>{dialogMode === 'create' ? 'Добавить сервер' : 'Редактировать сервер'}</DialogTitle>
        <Formik
          initialValues={editingServer || { fqdn: '', ip: '', status: 'available', server_type: '' }}
          validationSchema={ServerSchema}
          onSubmit={handleServerSubmit}
        >
          {({ values, handleChange, handleBlur, errors, touched, isSubmitting, setFieldValue }: {
            values: Server;
            handleChange: React.ChangeEventHandler;
            handleBlur: React.FocusEventHandler;
            errors: { fqdn?: string; ip?: string; status?: string; server_type?: string };
            touched: { fqdn?: boolean; ip?: boolean; status?: boolean; server_type?: boolean };
            isSubmitting: boolean;
            setFieldValue: (field: string, value: any) => void;
          }) => (
            <Form>
              <DialogContent>
                <TextField
                  fullWidth
                  id="fqdn"
                  name="fqdn"
                  label="FQDN"
                  value={values.fqdn}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={touched.fqdn && Boolean(errors.fqdn)}
                  helperText={touched.fqdn && errors.fqdn}
                  margin="normal"
                />
                <TextField
                  fullWidth
                  id="ip"
                  name="ip"
                  label="IP адрес"
                  value={values.ip}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={touched.ip && Boolean(errors.ip)}
                  helperText={touched.ip && errors.ip}
                  margin="normal"
                />
                <FormControl fullWidth margin="normal" error={touched.status && Boolean(errors.status)}>
                  <InputLabel id="status-label">Статус</InputLabel>
                  <Select
                    labelId="status-label"
                    id="status"
                    name="status"
                    value={values.status}
                    onChange={(e: SelectChangeEvent) => setFieldValue('status', e.target.value)}
                    onBlur={handleBlur}
                    label="Статус"
                  >
                    <MenuItem value="available">Доступен</MenuItem>
                    <MenuItem value="unavailable">Недоступен</MenuItem>
                  </Select>
                  {touched.status && errors.status && (
                    <FormHelperText>{errors.status}</FormHelperText>
                  )}
                </FormControl>
                <TextField
                  fullWidth
                  id="server_type"
                  name="server_type"
                  label="Тип сервера"
                  value={values.server_type}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  error={touched.server_type && Boolean(errors.server_type)}
                  helperText={touched.server_type && errors.server_type}
                  margin="normal"
                />
              </DialogContent>
              <DialogActions>
                <Button onClick={() => setServerDialogOpen(false)}>Отмена</Button>
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? <CircularProgress size={24} /> : 'Сохранить'}
                </Button>
              </DialogActions>
            </Form>
          )}
        </Formik>
      </Dialog>

      {/* Диалог подтверждения удаления */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Подтверждение удаления</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {deleteTarget.type === 'zone' && `Вы уверены, что хотите удалить зону "${deleteTarget.name}"? Все окружения и серверы внутри зоны также будут удалены.`}
            {deleteTarget.type === 'environment' && `Вы уверены, что хотите удалить окружение "${deleteTarget.name}"? Все серверы внутри окружения также будут удалены.`}
            {deleteTarget.type === 'server' && `Вы уверены, что хотите удалить сервер "${deleteTarget.name}"?`}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Отмена</Button>
          <Button onClick={handleDeleteConfirm} color="error">
            Удалить
          </Button>
        </DialogActions>
      </Dialog>

      {/* Уведомление */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default MainPage; 