import React from 'react';
import axios from 'axios';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TablePagination from '@material-ui/core/TablePagination';
import TableRow from '@material-ui/core/TableRow';
import TableSortLabel from '@material-ui/core/TableSortLabel';
import Paper from '@material-ui/core/Paper';
import Checkbox from '@material-ui/core/Checkbox';
import CircularProgress from '@material-ui/core/CircularProgress';

import TableToolBar from './TableToolBar';
import DeleteDialog from './DeletePopup';
import RDBTableHead from './RDBTableHead';
import { RDBChartStyles } from './Styles';
import { getComparator, stableSort, Order } from './HelperFunctions';

interface PAProps {
    alias: string;
    ar: string;
    catalog: string;
    date: string;
    description: string;
    fullname: string;
    incub: Array<number>;
    incubS: Array<number>;
    is_factory: boolean;
    source: string;
    volume: number;
}

interface HeadCell {
    disablePadding: boolean,
    id: keyof PAProps,
    label: string;
    numeric: boolean;
}

const headCells: HeadCell[] = [
    { id: 'alias', numeric: false, disablePadding: true, label: 'Alias' },
    { id: 'catalog', numeric: false, disablePadding: false, label: 'Catalog' },
    { id: 'ar', numeric: false, disablePadding: false, label: 'AR' },
    { id: 'incub', numeric: true, disablePadding: false, label: 'Titan Incubation' },
    { id: 'incubS', numeric: true, disablePadding: false, label: 'Titan-S Incubation' },
    { id: 'fullname', numeric: false, disablePadding: false, label: 'Full Name' },
    { id: 'is_factory', numeric:false, disablePadding: false, label: 'Factory' },
];

interface PATableProps {
    classes: ReturnType<typeof RDBChartStyles>;
    numSelected: number;
    onRequestSort: (event: React.MouseEvent<unknown>, property: keyof PAProps) => void;
    onSelectAllClick: (event: React.ChangeEvent<HTMLInputElement>) => void;
    order: Order;
    orderBy: string;
    rowCount: number;
}

function ReagentTableHead(props: PATableProps) {
    const { classes, onSelectAllClick, order, orderBy, numSelected, rowCount, onRequestSort } = props;
    const createSortHandler = (property: keyof PAProps) => (event: React.MouseEvent<unknown>) => {
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

export default function PA() {
    const classes = RDBChartStyles();
    const [order, setOrder] = React.useState<Order>('asc');
    const [orderBy, setOrderBy] = React.useState<keyof PAProps>('catalog');
    const [selected, setSelected] = React.useState<string[]>([]);
    const [page, setPage] = React.useState(0);
    const [rowsPerPage, setRowsPerPage] = React.useState(10);
    const [PAList, setPAList] = React.useState<PAProps[]>([]);
    const [loading, setLoading] = React.useState(true);
    const [showDeleteDialog, setShowDeleteDialog] = React.useState(false);

    React.useEffect(() => {
        axios.get<PAProps[]>('api/pa/')
        .then((res) => {
            const serverPA = res.data.map((obj, index)=> ({...obj, id: index}));
            setPAList(serverPA);
        })
        .catch((err) => { 
            console.log(err); 
        });
        return () => {
            setLoading(false);
        }
    });

    const handleRequestSort = (event: React.MouseEvent<unknown>, property: keyof PAProps) => {
        const isAsc = orderBy === property && order === 'asc';
        setOrder(isAsc ? 'desc' : 'asc');
        setOrderBy(property);
    };

    const handleSelectAllClick = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.checked) {
            const newSelecteds = PAList.map((n) => n.catalog);
            setSelected(newSelecteds);
            return;
        }
        setSelected([]);
    }

    const handleClick = (event: React.MouseEvent<unknown>, name: string) => {
        const selectedIndex = selected.indexOf(name);
        let newSelected: string[] = [];

        if (selectedIndex === -1) {
            newSelected = newSelected.concat(selected, name);
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
    const emptyRows = rowsPerPage - Math.min(rowsPerPage, PAList.length - page * rowsPerPage);

    return (
        <div className={classes.root}>
            <Paper className={classes.paper}>
                <TableToolBar numSelected={selected.length} 
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
                            rowCount={PAList.length}
                        />
                        <TableBody>
                            {loading ? 
                                <TableRow style={{ height: 53 * emptyRows }}>
                                    <TableCell align="center" colSpan={8}>
                                        <CircularProgress /> 
                                    </TableCell>
                                </TableRow>
                                : stableSort(PAList, getComparator(order, orderBy))
                                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                                .map((row, index) => {
                                    const isItemSelected = isSelected(row.catalog);
                                    const labelId = `enhanced-table-checkbox-${index}`;

                                    return (
                                        <TableRow
                                            hover
                                            onClick={(event) => handleClick(event, row.catalog)}
                                            role="checkbox"
                                            aria-checked={isItemSelected}
                                            tabIndex={-1}
                                            key={row.catalog}
                                            selected={isItemSelected}
                                        >
                                            <TableCell padding="checkbox">
                                                <Checkbox
                                                    checked={isItemSelected}
                                                    inputProps={{ 'aria-labelledby': labelId }}
                                                />
                                            </TableCell>
                                            <TableCell component="th" id={labelId} scope="row" padding="none">
                                                {row.alias}
                                            </TableCell>
                                            <TableCell align="right">{row.catalog}</TableCell>
                                            <TableCell align="right">{row.ar}</TableCell>
                                            <TableCell align="right">{row.incub[0]}</TableCell>
                                            <TableCell align="right">{row.incub[1]}</TableCell>
                                            <TableCell align="right">{row.fullname}</TableCell>
                                            <TableCell align="right">{row.is_factory ? <>yes</> : <>no</>}</TableCell>
                                        </TableRow>
                                    );
                                    {emptyRows > 0 && (
                                        <TableRow style={{ height: 53 * emptyRows }}>
                                            <TableCell colSpan={8}/>
                                        </TableRow>)
                                    }
                                })}
                        </TableBody>
                    </Table>
                </TableContainer>
                <TablePagination
                    rowsPerPageOptions={[10, 25, 50]}
                    component="div"
                    count={PAList.length}
                    rowsPerPage={rowsPerPage}
                    page={page}
                    onChangePage={handleChangePage}
                    onChangeRowsPerPage={handleChangeRowsPerPage}
                />
            </Paper>
            <DeleteDialog serialNos={selected} open={showDeleteDialog} setOpen={setShowDeleteDialog} dataType={"pa"}/>
        </div>
    );
}