import React from 'react';
import clsx from 'clsx';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import { useTheme } from '@material-ui/core/styles';
import { CssBaseline, Drawer, IconButton } from '@material-ui/core';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import Divider from '@material-ui/core/Divider';
import MenuIcon from '@material-ui/icons/Menu';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import ChevronRightIcon from '@material-ui/icons/ChevronRight';
import GitHubIcon from '@material-ui/icons/GitHub';
import EmojiFoodBeverageIcon from '@material-ui/icons/EmojiFoodBeverage';
import AndroidIcon from '@material-ui/icons/Android';
import SentimentVerySatisfiedIcon from '@material-ui/icons/SentimentVerySatisfied';

import {Route, Link, HashRouter} from 'react-router-dom';

import { useStyles } from './Styles';
import PA from './PA';
import Reagent from './Reagent';

export default function Dashboard() {
    const classes = useStyles();
    const theme = useTheme();
    const [open, setOpen] = React.useState(false);

    function RenderDrawerIcons() {
        const drawerItems = [{text: 'PA', icon: (<GitHubIcon/>)},
            {text: 'Reagents', icon: (<EmojiFoodBeverageIcon/>)},
            {text: 'Autostainers', icon: (<AndroidIcon/>)}];

        return drawerItems.map((obj) => 
            <ListItem button key={obj.text} component={Link} to={obj.text}>
                <ListItemIcon>{obj.icon}</ListItemIcon>
                <ListItemText primary={obj.text}/>
            </ListItem>
        );
    }

    const handleDrawerOpen = () => {
        setOpen(true);
    };

    const handleDrawerClose = () => {
        setOpen(false);
    };

    return(
    <div className={classes.root}>
    <HashRouter>
        <CssBaseline />
        <AppBar
            position="fixed"
            className={clsx(classes.appBar, {
                [classes.appBarShift]: open,
            })}
        >
            <Toolbar>
                <IconButton
                    color="inherit"
                    aria-label="open drawer"
                    onClick={handleDrawerOpen}
                    edge="start"
                    className={clsx(classes.menuButton, {
                        [classes.hide]: open,
                    })}
                >
                    <MenuIcon />
                </IconButton>
                <Typography variant="h6" noWrap>
                    Mini variant drawer
                </Typography>
            </Toolbar>
        </AppBar>
        <Drawer
            variant="permanent"
            className={clsx(classes.drawer, {
                [classes.drawerOpen] : open,
                [classes.drawerClose]: !open,
            })}
            classes={{
                paper: clsx({
                    [classes.drawerOpen]: open,
                    [classes.drawerClose]: !open,
                }),
            }}
        >
            <div className={classes.toolbar}>
                <IconButton onClick={handleDrawerClose}>
                    {theme.direction === 'rtl' ? <ChevronRightIcon /> : <ChevronLeftIcon />}
                </IconButton>
            </div>
            <Divider/>
                <List>
                    { RenderDrawerIcons() }
                </List>
                <div>
                </div>
            <Divider />
            <List>
                {['Other', 'Settings'].map((text, index) => (
                    <ListItem button key={text}>
                        <ListItemIcon>{index % 2 === 0 ? <SentimentVerySatisfiedIcon/> : <SentimentVerySatisfiedIcon />}</ListItemIcon>
                        <ListItemText primary={text} />
                    </ListItem>
                ))}
            </List>
        </Drawer>
        <main className={classes.content}>
            <div className={classes.toolbar}/>
            <Route path="/PA" component={PA}/>
            <Route path="/Reagents" component={Reagent}/>
        </main>
    </HashRouter>
    </div>
    );
}