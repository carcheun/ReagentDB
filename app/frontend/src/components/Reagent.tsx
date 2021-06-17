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

export default function Reagent(props: any) {
    let v = props.nothing;

    const classes = RDBChartStyles();
    const [order, setOrder] = React.useState<Order>('asc');
    const [selected, setSelected] = React.useState<string[]>([]);
    const [selectedSN, setSelectedSN] = React.useState<string[]>([]);
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
                <TableToolBar 
                    numSelected={selected.length} 
                    setOpen={setShowDeleteDialog} />
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
            <DeleteDialog serialNos={selectedSN} open={showDeleteDialog} setOpen={setShowDeleteDialog} dataType={"reagent"}/>
        </div>
    );
}