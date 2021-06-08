import React from 'react';
import clsx from 'clsx';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import { createStyles, makeStyles, useTheme, Theme } from '@material-ui/core/styles';
import { CssBaseline, SwipeableDrawer, IconButton } from '@material-ui/core';
import List from '@material-ui/core/List';
import Divider from '@material-ui/core/Divider';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import InboxIcon from '@material-ui/icons/MoveToInbox';
import MailIcon from '@material-ui/icons/Mail';
import GitHubIcon from '@material-ui/icons/GitHub';
import MenuIcon from '@material-ui/icons/Menu';
import EmojiFoodBeverageIcon from '@material-ui/icons/EmojiFoodBeverage';
import AndroidIcon from '@material-ui/icons/Android';
import SentimentVerySatisfiedIcon from '@material-ui/icons/SentimentVerySatisfied';

import PA from './PA'

const useStyles = makeStyles((theme: Theme) => 
    createStyles({
        root: {
            display: 'flex',
        },
        list: {
            padding: theme.spacing(0,1),
            width: 250,
        },
        appBar: {
            zIndex: theme.zIndex.drawer + 1,
        },
        toolBar: {
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-end',
            padding: theme.spacing(0,1),
            // necessary for content to be below app bar
            ...theme.mixins.toolbar,
        },
        menuButton: {
            marginRight: theme.spacing(2),
        },
        content: {
            flexGrow: 1,
            padding: theme.spacing(3),
        },
        offset: {...theme.mixins.toolbar},
    }),
);

type Anchor = 'left';

function RenderDrawerIcons() {
    const drawerItems = [{text: 'PA', icon: (<GitHubIcon/>)},
        {text: 'Reagents', icon: (<EmojiFoodBeverageIcon/>)},
        {text: 'Autostainers', icon: (<AndroidIcon/>)}];

    return drawerItems.map((obj) => 
        <ListItem button key={obj.text}>
            <ListItemIcon>{obj.icon}</ListItemIcon>
            <ListItemText primary={obj.text}/>
        </ListItem>
    );
}


const SwipeableTemporaryDrawer = () => {
  const classes = useStyles();
  const theme = useTheme();
  const [state, setState] = React.useState({
    left: false,
  })



  const toggleDrawer = (anchor: Anchor, open: boolean) => (
    event: React.KeyboardEvent | React.MouseEvent,
  ) => {
    if (
      event &&
      event.type === 'keydown' &&
      ((event as React.KeyboardEvent).key === 'Tab' ||
        (event as React.KeyboardEvent).key === 'Shift')
    ) {
      return
    }

    setState({ ...state, [anchor]: open });
  }

  const list = (anchor: Anchor) => (
    <div
        className={clsx(classes.list)}
        role="presentation"
        onClick={toggleDrawer(anchor, false)}
        onKeyDown={toggleDrawer(anchor, false)}
    >
        <List>
            { RenderDrawerIcons() }
        </List>
        <Divider />
            <List>
                {['All mail', 'Trash', 'Spam'].map((text, index) => (
                <ListItem button key={text}>
                    <ListItemIcon>{index % 2 === 0 ? <InboxIcon /> : <MailIcon />}</ListItemIcon>
                    <ListItemText primary={text} />
                </ListItem>
                ))}
            </List>
    </div>
  )

  return (
    <div className={classes.root}>
    <CssBaseline />
    <AppBar position="fixed"
        className={classes.appBar}>
    <Toolbar>
        {(['left'] as Anchor[]).map((anchor) => (
        <React.Fragment key={anchor}>
            <IconButton 
                color="inherit"
                aria-label="open drawer"
                edge="start"
                className={clsx(classes.menuButton)}
                onClick={toggleDrawer(anchor, true)}>
                <MenuIcon />
            </IconButton>
            <SwipeableDrawer
                anchor={anchor}
                open={state[anchor]}
                onClose={toggleDrawer(anchor, false)}
                onOpen={toggleDrawer(anchor, true)}
                >
                {list(anchor)}
            </SwipeableDrawer>
        </React.Fragment>
        ))}
    </Toolbar>
    </AppBar>
        <main className={clsx(classes.content)}>
            <div className={clsx(classes.toolBar)}>
                <PA/>
            </div>
        </main>
    </div>
  )
}


export default SwipeableTemporaryDrawer;