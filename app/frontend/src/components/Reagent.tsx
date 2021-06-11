import React from 'react';
import axios from 'axios'
import { DataGrid, GridColDef } from '@material-ui/data-grid';

const columns: GridColDef[] = [
    {field: 'id', headerName: 'ID', width: 130, hide: true},
    {field: 'reag_name', headerName: 'Reagent', width: 250 },
    {field: 'reagent_sn', headerName: 'SN', width: 250},
    {field: 'catalog', headerName: 'Catalog', width: 200},
    {field: 'vol_cur', headerName: 'Volume', type: 'number', width: 180},
    {field: 'mfg_date', headerName: 'Manufacture Date', width: 250},
    {field: 'exp_date', headerName: 'Expire Date', width: 250}
];

interface ReagentProperties {
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

export default function Reagent() {
    const [ReagentList, setReagentList] = React.useState<ReagentProperties[]>([]);
    const [loading, setLoading] = React.useState(true);

    React.useEffect(() => {
        axios.get<ReagentProperties[]>('api/reagent/')
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

    return(
    <div style={{height: 800, width: '100%'}}>
        <DataGrid rows={ReagentList} columns={columns} pageSize={25} checkboxSelection loading={loading}/>
    </div>
    );
}