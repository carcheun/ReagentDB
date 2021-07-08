import React from 'react';
import axios from 'axios';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TablePagination from '@material-ui/core/TablePagination';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';
import Checkbox from '@material-ui/core/Checkbox';
import CircularProgress from '@material-ui/core/CircularProgress';
import EditIcon from '@material-ui/icons/Edit';
import LinearProgress from '@material-ui/core/LinearProgress';
import ErrorIcon from '@material-ui/icons/Error';
import Tooltip from '@material-ui/core/Tooltip';
import { makeStyles, createStyles, Theme } from '@material-ui/core/styles';

import { RDBChartStyles } from './Styles';
import DeleteDialog from './DeletePopup';
import TableToolBar from './TableToolBar';
import RDBTableHead from './RDBTableHead';
import { getComparator, stableSort, Order } from './HelperFunctions';

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

const useStyles = makeStyles((theme: Theme) =>
    createStyles({
        root: {
            height: 7,
            borderRadius: 3,
        },
        colorPrimary: {
            backgroundColor: theme.palette.grey[theme.palette.type === 'light' ? 200 : 700],
        },
        barGreen: {
            borderRadius: 3,
            backgroundColor: '#4CAF50',
        },
        barYellow: {
            borderRadius: 3,
            backgroundColor: '#FFEB3B',
        },
        barRed: {
            borderRadius: 3,
            backgroundColor: '#d32f2f',
        },
    }),
);

const BorderLinearProgress = (props: any) => {
    const classes = useStyles();
    const { percentage } = props;
    if (percentage > 60) {
        return (
            <LinearProgress variant="determinate" classes={{root: classes.root, colorPrimary: classes.colorPrimary, bar: classes.barGreen}} value={percentage}></LinearProgress>
        );
    } else if (percentage > 30) {
        return (
            <LinearProgress variant="determinate" classes={{root: classes.root, colorPrimary: classes.colorPrimary, bar: classes.barYellow}} value={percentage}></LinearProgress>
        );
    } else {
        return (
            <LinearProgress variant="determinate" classes={{root: classes.root, colorPrimary: classes.colorPrimary, bar: classes.barRed}} value={percentage}></LinearProgress>
        );
    }
}

export default function Reagent(props: any) {
    const classes = RDBChartStyles();
    const [order, setOrder] = React.useState<Order>('asc');
    const [selected, setSelected] = React.useState<string[]>([]);
    const [page, setPage] = React.useState(0);
    const [rowsPerPage, setRowsPerPage] = React.useState(10);
    const [loading, setLoading] = React.useState(true);
    const [showDeleteDialog, setShowDeleteDialog] = React.useState(false);
    const [orderBy, setOrderBy] = React.useState<keyof ReagentProps>('reag_name');
    const [ReagentList, setReagentList] = React.useState<ReagentProps[]>([]);

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
            const newSelecteds = ReagentList.map((n) => n.reagent_sn);
            setSelected(newSelecteds);
            return;
        }
        setSelected([]);
    };

    const handleClick = (event: React.MouseEvent<unknown>, sn: string) => {
        const selectedIndex = selected.indexOf(sn);
        let newSelected: string[] = [];

        console.log(selectedIndex);

        if (selectedIndex === -1) {
            newSelected = newSelected.concat(selected, sn);
        } else if (selectedIndex === 0) {
            newSelected = newSelected.concat(selected.slice(1));
        } else if (selectedIndex === selected.length - 1) {
            newSelected = newSelected.concat(selected.slice(0, -1));
        } else if (selectedIndex > 0) {
            newSelected = newSelected.concat(
                selected.slice(0, selectedIndex),
                selected.slice(selectedIndex + 1),
            );
        }

        setSelected(newSelected);
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
    const todayDate = new Date();

    return (
        <div className={classes.root}>
            <Paper className={classes.paper}>
                <TableToolBar 
                    numSelected={selected.length} 
                    setOpen={setShowDeleteDialog}
                    toolTitle={"Reagent"}
                    setClear={setSelected} />
                <TableContainer>
                    <Table
                        className={classes.table}
                        aria-labelledby="tableTitle"
                        aria-label="reagent table"
                    >
                        <RDBTableHead
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
                                        const isItemSelected = isSelected(row.reagent_sn);
                                        const labelId = `enhanced-table-checkbox-${index}`;
                                        let isExpired = false;
                                        if (todayDate > new Date(row.exp_date)) {
                                            isExpired = true;
                                        }

                                        return (
                                            <TableRow
                                                hover
                                                onClick={(event) => handleClick(event, row.reagent_sn)}
                                                role="checkbox"
                                                aria-checked={isItemSelected}
                                                tabIndex={-1}
                                                key={row.reagent_sn}
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
                                                <TableCell align="right">
                                                    {row.vol_cur} / {row.vol}
                                                    <br />
                                                    <BorderLinearProgress percentage={(row.vol_cur / row.vol) * 100}/>    
                                                </TableCell>
                                                <TableCell align="right">{row.r_type}</TableCell>
                                                <TableCell align="right">{row.log}</TableCell>
                                                <TableCell align="right">{row.mfg_date}</TableCell>
                                                <TableCell align="right">
                                                    {isExpired ? 
                                                    <Tooltip title="Expired" aria-label="expired">
                                                        <ErrorIcon fontSize="small" style={{ color: "#d32f2f"}}/> 
                                                    </Tooltip> :
                                                        <></> }{row.exp_date}
                                                </TableCell>
                                                <TableCell align="right">{row.factory ? <>yes</> : <>no</>}</TableCell>
                                                <TableCell>
                                                    <EditIcon></EditIcon>
                                                </TableCell>
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
            <DeleteDialog serialNos={selected} open={showDeleteDialog} setOpen={setShowDeleteDialog} dataType={"reagent"}/>
        </div>
    );
}