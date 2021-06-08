import React from 'react';
import axios from 'axios'
import { DataGrid, GridColDef } from '@material-ui/data-grid';

import { useStyles } from './Styles';

const columns: GridColDef[] = [
    {field: 'id', headerName: 'ID', width: 130, hide: true},
    {field: 'fullname', headerName: 'Full name', width: 250 },
    {field: 'alias', headerName: 'Alias', width: 250},
    {field: 'catalog', headerName: 'Catalog', width: 200},
    {field: 'incub', headerName: 'Incubation', type: 'array', width: 180},
    {field: 'ar', headerName: 'AR', width: 130},
    {field: 'is_factory', headerName: 'Factory', width: 130, type: 'boolean'}
];

interface PAProperties {
    alias: string;
    ar: string;
    catalog: string;
    date: string;
    description: string;
    fullname: string;
    incub: Array<number>;
    is_factory: boolean;
    source: string;
    volume: number;
}

export default function PA() {
    const classes = useStyles();
    const [PAList, setPAList] = React.useState<PAProperties[]>([]);
    const [loading, setLoading] = React.useState<boolean>(true);

    React.useEffect(() => {
        axios.get<PAProperties[]>('api/pa/')
        .then((res) => {
            const serverPA = res.data.map((obj, index)=> ({...obj, id: index}));
            setPAList(serverPA);
            setLoading(false);
        })
        .catch((err) => { 
            console.log(err); 
            setLoading(false);
        });
    });
    return(
    <div style={{height: 800, width: '100%'}}>
        <DataGrid rows={PAList} columns={columns} pageSize={25} checkboxSelection loading={loading} />
    </div>
    );
}