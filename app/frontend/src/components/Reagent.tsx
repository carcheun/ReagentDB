import React from 'react';
import clsx from 'clsx';
import axios from 'axios';
import Tooltip from '@material-ui/core/Tooltip';
import Toolbar from '@material-ui/core/Toolbar';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TablePagination from '@material-ui/core/TablePagination';
import TableRow from '@material-ui/core/TableRow';
import TableSortLabel from '@material-ui/core/TableSortLabel';
import Typography from '@material-ui/core/Typography';
import Paper from '@material-ui/core/Paper';
import Checkbox from '@material-ui/core/Checkbox';
import { createStyles, lighten, makeStyles, Theme } from '@material-ui/core/styles';
import IconButton from '@material-ui/core/IconButton';
import DeleteIcon from '@material-ui/icons/Delete';
import FilterListIcon from '@material-ui/icons/FilterList';
import CircularProgress from '@material-ui/core/CircularProgress';

import DeleteDialog from './DeletePopup';
import { SettingsPowerRounded } from '@material-ui/icons';

interface ReagentProps {
    reag_name: string;
    size: string;
    log: string;
    reagent_sn: string;
    vol_cur: number;
    vol: number;
    sequence: string;
    catalog: string;
    date: string;
    mfg_date: string;
    exp_date: string;
    r_type: string;
    factory: boolean;
    autostainer_sn: number;
    in_use: boolean;
}

interface HeadCell {
    disablePadding: boolean,
    id: keyof ReagentProps,
    label: string;
    numeric: boolean;
}

interface TableToolbarProps {
    numSelected: number;
    selectedSN: string[];
    setOpen: any;
}

const headCells: HeadCell[] = [
    { id: 'reag_name', numeric: false, disablePadding: true, label: 'Reagent' },
    { id: 'reagent_sn', numeric: false, disablePadding: false, label: 'Serial Number' },
    { id: 'catalog', numeric: false, disablePadding: false, label: 'Catalog' },
    { id: 'vol', numeric: true, disablePadding: false, label: 'Volumne (μL)' },
    { id: 'r_type', numeric: false, disablePadding: false, label: 'Type' },
    { id: 'log', numeric: false, disablePadding: false, label: 'Lot' },
    { id: 'mfg_date', numeric: false, disablePadding: false, label: 'Manufacture Date' },
    { id: 'exp_date', numeric: false, disablePadding: false, label: 'Expire Date' },
    { id: 'factory', numeric: false, disablePadding: false, label: 'Factory' },
];

interface ReagentTableProps {
    classes: ReturnType<typeof useStyles>;
    numSelected: number;
    onRequestSort: (event: React.MouseEvent<unknown>, property: keyof ReagentProps) => void;
    onSelectAllClick: (event: React.ChangeEvent<HTMLInputElement>) => void;
    order: Order;
    orderBy: string;
    rowCount: number;
}

function ReagentTableHead(props: ReagentTableProps) {
    const { classes, onSelectAllClick, order, orderBy, numSelected, rowCount, onRequestSort } = props;
    const createSortHandler = (property: keyof ReagentProps) => (event: React.MouseEvent<unknown>) => {
        onRequestSort(event, property);
    };

    return (
        <TableHead>
            <TableRow>
                <TableCell padding="checkbox">
                    <Checkbox
                        indeterminate={ numSelected > 0 && numSelected < rowCount }
                        checked={rowCount > 0 && numSelected === rowCount }
                        onChange={onSelectAllClick}
                        inputProps={{ 'aria-label': 'select all reagents' }}
                    />
                </TableCell>
                {headCells.map((headCell) => (
                    <TableCell
                        key={headCell.id}
                        align={headCell.numeric ? 'right' : 'right'}
                        padding={headCell.disablePadding ? 'none' : 'default'}
                        sortDirection={orderBy === headCell.id ? order : false }
                        >
                        <TableSortLabel
                            active={orderBy === headCell.id}
                            direction={orderBy === headCell.id ? order: 'asc'}
                            onClick={createSortHandler(headCell.id)}
                        >
                            {headCell.label}
                            {orderBy === headCell.id ? (
                                <span className={classes.visuallyHidden}>
                                    {order === 'desc' ? 'sorted descending' : 'sorted ascending'}
                                </span>
                            ): null }
                        </TableSortLabel>
                    </TableCell>
                ))}
            </TableRow>
        </TableHead>
    );
}

const useToolbarStyles = makeStyles((theme: Theme) =>
    createStyles({
        root: {
            paddingLeft: theme.spacing(2),
            paddingRight: theme.spacing(1),
        },
        highlight:
            theme.palette.type === 'light'
                ? {
                    color: theme.palette.secondary.main,
                    backgroundColor: lighten(theme.palette.secondary.light, 0.85),
                }
                : {
                    color: theme.palette.text.primary,
                    backgroundColor: theme.palette.secondary.dark,
                },
        title : {
            flex: '1 1 100%',
        },
    }),
);

const ReagentTableToolbar = (props: TableToolbarProps) => {
    const classes = useToolbarStyles();
    const { numSelected, selectedSN, setOpen } = props;

    const handleDelete = () => {
        setOpen(true);
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
                    Reagents
                </Typography>
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

function descendingComparator<T>(a: T, b: T, orderBy: keyof T) {
    if (b[orderBy] < a[orderBy]) {
        return -1;
    }
    if (b[orderBy] > a[orderBy]) {
        return 1;
    }
    return 0;
}

type Order = 'asc' | 'desc';

function getComparator<Key extends keyof any>(
    order: Order,
    orderBy: Key,
) : (a: { [key in Key]: number | string | boolean}, b: {[key in Key]: number | string | boolean}) => number {
    return order === 'desc'
        ? (a,b) => descendingComparator(a, b, orderBy)
        : (a,b) => -descendingComparator(a, b, orderBy);
}

function stableSort<T>(array: T[], comparator: (a: T, b: T) => number) {
    const stabilizedThis = array.map((el, index) => [el, index] as [T, number]);
    stabilizedThis.sort((a,b) => {
        const order = comparator(a[0], b[0]);
        if (order !== 0) return order;
        return a[1] - b[1];
    });
    return stabilizedThis.map((el) => el[0]);
}

const useStyles = makeStyles((theme: Theme) => 
    createStyles({
        root: {
            width: '100%',
        },
        paper: {
            width: '100%',
            margin: theme.spacing(2),
        },
        table: {
            minWidth: 750,
        },
        visuallyHidden: {
            border: 0,
            clip: 'rect(0,0,0,0)',
            height: 1,
            margin: -1,
            overflow: 'hidden',
            padding: 0,
            position: 'absolute',
            top: 20,
            width: 1,
        }
    }),
);

export default function Reagent() {
    const classes = useStyles();
    const [order, setOrder] = React.useState<Order>('asc');
    const [orderBy, setOrderBy] = React.useState<keyof ReagentProps>('reag_name');
    const [selected, setSelected] = React.useState<string[]>([]);
    const [selectedSN, setSelectedSN] = React.useState<string[]>([]);
    const [page, setPage] = React.useState(0);
    const [rowsPerPage, setRowsPerPage] = React.useState(10);
    const [ReagentList, setReagentList] = React.useState<ReagentProps[]>([]);
    const [loading, setLoading] = React.useState(true);
    const [showDeleteDialog, setShowDeleteDialog] = React.useState(false);

    React.useEffect(() => {
        axios.get<ReagentProps[]>('api/reagent/')
        .then((res) => {
            const ReagentList = res.data.map((obj, index)=> ({...obj, id: index}));
            setReagentList(ReagentList);
        })
        .catch((err) => { 
            console.log(err); 
        });
        return () => {
            setLoading(false);
        }
    });

    const handleRequestSort = (event: React.MouseEvent<unknown>, property: keyof ReagentProps) => {
        const isAsc = orderBy === property && order === 'asc';
        setOrder(isAsc ? 'desc' : 'asc');
        setOrderBy(property);
    };

    const handleSelectAllClick = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.checked) {
            const newSelecteds = ReagentList.map((n) => n.reag_name);
            const newSNSelecteds = ReagentList.map((n) => n.reagent_sn);
            setSelected(newSelecteds);
            setSelectedSN(newSNSelecteds);
            return;
        }
        setSelected([]);
        setSelectedSN([]);
    };

    const handleClick = (event: React.MouseEvent<unknown>, name: string, sn: string) => {
        const selectedIndex = selected.indexOf(name);
        let newSelected: string[] = [];
        let newSNSelected: string[] = [];

        if (selectedIndex === -1) {
            newSelected = newSelected.concat(selected, name);
            newSNSelected = newSNSelected.concat(selectedSN, sn);
        } else if (selectedIndex === 0) {
            newSelected = newSelected.concat(selected.slice(1));
            newSNSelected = newSNSelected.concat(selectedSN.slice(1));
        } else if (selectedIndex === selected.length - 1) {
            newSelected = newSelected.concat(selected.slice(0, -1));
            newSNSelected = newSNSelected.concat(selectedSN.slice(0, -1));
        } else if (selectedIndex > 0) {
            newSelected = newSelected.concat(
                selected.slice(0, selectedIndex),
                selected.slice(selectedIndex + 1),
            );
            newSNSelected = newSNSelected.concat(
                selectedSN.slice(0, selectedIndex),
                selectedSN.slice(selectedIndex + 1),
            );
        }

        setSelected(newSelected);
        setSelectedSN(newSNSelected);
    };

    const handleChangePage = (event: unknown, newPage: number) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    const isSelected = (name: string) => selected.indexOf(name) !== -1;
    const emptyRows = rowsPerPage - Math.min(rowsPerPage, ReagentList.length - page * rowsPerPage);

    return (
        <div className={classes.root}>
            <Paper className={classes.paper}>
                <ReagentTableToolbar 
                    numSelected={selected.length} 
                    selectedSN={selectedSN}
                    setOpen={setShowDeleteDialog} />
                <TableContainer>
                    <Table
                        className={classes.table}
                        aria-labelledby="tableTitle"
                        aria-label="reagent table"
                    >
                        <ReagentTableHead
                            classes={classes}
                            numSelected={selected.length}
                            order={order}
                            orderBy={orderBy}
                            onSelectAllClick={handleSelectAllClick}
                            onRequestSort={handleRequestSort}
                            rowCount={ReagentList.length}
                        />
                        <TableBody>
                            {loading ? 
                                <TableRow style={{ height: 53 * emptyRows }}>
                                    <TableCell align="center" colSpan={10}>
                                        <CircularProgress /> 
                                    </TableCell>
                                </TableRow> 
                                : stableSort(ReagentList, getComparator(order, orderBy))
                                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                                    .map((row, index) => {
                                        const isItemSelected = isSelected(row.reag_name);
                                        const labelId = `enhanced-table-checkbox-${index}`;

                                        return (
                                            <TableRow
                                                hover
                                                onClick={(event) => handleClick(event, row.reag_name, row.reagent_sn)}
                                                role="checkbox"
                                                aria-checked={isItemSelected}
                                                tabIndex={-1}
                                                key={row.reag_name}
                                                selected={isItemSelected}
                                            >
                                                <TableCell padding="checkbox">
                                                    <Checkbox
                                                        checked={isItemSelected}
                                                        inputProps={{ 'aria-labelledby': labelId }}
                                                    />
                                                </TableCell>
                                                <TableCell component="th" id={labelId} scope="row" padding="none">
                                                    {row.reag_name}
                                                </TableCell>
                                                <TableCell align="right">{row.reagent_sn}</TableCell>
                                                <TableCell align="right">{row.catalog}</TableCell>
                                                <TableCell align="right">{row.vol_cur} / {row.vol}</TableCell>
                                                <TableCell align="right">{row.r_type}</TableCell>
                                                <TableCell align="right">{row.log}</TableCell>
                                                <TableCell align="right">{row.mfg_date}</TableCell>
                                                <TableCell align="right">{row.exp_date}</TableCell>
                                                <TableCell align="right">{row.factory ? <>yes</> : <>no</>}</TableCell>
                                            </TableRow>
                                        );
                                        {emptyRows > 0 && (
                                            <TableRow style={{ height: 53 * emptyRows }}>
                                                <TableCell colSpan={10}/>
                                            </TableRow>
                                        )}
                                })
                            }
                        </TableBody>
                    </Table>
                </TableContainer>
                <TablePagination
                    rowsPerPageOptions={[10, 25, 50]}
                    component="div"
                    count={ReagentList.length}
                    rowsPerPage={rowsPerPage}
                    page={page}
                    onChangePage={handleChangePage}
                    onChangeRowsPerPage={handleChangeRowsPerPage}
                />
            </Paper>
            <DeleteDialog serial_nos={selectedSN} open={showDeleteDialog} setOpen={setShowDeleteDialog}/>
        </div>
    );
}