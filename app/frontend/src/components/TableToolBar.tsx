import clsx from 'clsx';
import Tooltip from '@material-ui/core/Tooltip';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import DeleteIcon from '@material-ui/icons/Delete';
import ClearIcon from '@material-ui/icons/Clear';
import FilterListIcon from '@material-ui/icons/FilterList';

import { useToolbarStyles} from './Styles';

interface TableToolbarProps {
    numSelected: number;
    setOpen: any;
    toolTitle: string;
    setClear: any;
}

export default function TableToolBar(props: TableToolbarProps) {
    // TODO: tool bar only says REAGENTS right now, change it to reflect a variable
    const classes = useToolbarStyles();
    const { numSelected, setOpen, toolTitle, setClear } = props;

    const handleDelete = () => {
        setOpen(true);
    }

    const handleClear = () => {
        setClear([])
    }

    return (
        <Toolbar
            className={clsx(classes.root, {
                [classes.highlight]: numSelected > 0,
            })}
        >
            {numSelected > 0 ? (
                <Typography className={classes.title} color="inherit" variant="subtitle1" component="div">
                    {numSelected} selected
                </Typography>
            ) : (
                <Typography className={classes.title} variant="h6" id="tableTitle" component="div">
                    {toolTitle}
                </Typography>
            )}
            {numSelected > 0 && (
                <Tooltip title="Cancel">
                    <IconButton aria-label="clear" onClick={handleClear}>
                        <ClearIcon/>
                    </IconButton>
                </Tooltip>
            )}
            {numSelected > 0 ? (
                <Tooltip title="Delete">
                    <IconButton aria-label="delete" onClick={handleDelete}>
                        <DeleteIcon/>
                    </IconButton>
                </Tooltip>
            ) : (
                <Tooltip title="Filter list">
                    <IconButton aria-label="filter list">
                        <FilterListIcon />
                    </IconButton>
                </Tooltip>
            )}
        </Toolbar>
    );
}