
import React from 'react';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TableSortLabel from '@material-ui/core/TableSortLabel';
import Checkbox from '@material-ui/core/Checkbox';


import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';

import { Order } from './HelperFunctions';
import { RDBChartStyles } from './Styles';

interface HeadCell {
    disablePadding: boolean,
    id: keyof ReagentProps,
    label: string;
    numeric: boolean;
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

interface ReagentTableProps {
    classes: ReturnType<typeof RDBChartStyles>;
    numSelected: number;
    onRequestSort: (event: React.MouseEvent<unknown>, property: keyof ReagentProps) => void;
    onSelectAllClick: (event: React.ChangeEvent<HTMLInputElement>) => void;
    order: Order;
    orderBy: string;
    rowCount: number;
}

export default function RDBTableHead(props: ReagentTableProps) {
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
                        align={headCell.id === 'reag_name' ? 'left' : 'right'}
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
                <TableCell padding="checkbox">

                </TableCell>
            </TableRow>
        </TableHead>
    );
}
