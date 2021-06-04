import React, { Component } from 'react';
import axios from 'axios'
import { DataGrid, GridColDef, GridValueGetterParams } from '@material-ui/data-grid';

//const rows = [
//    {id: 1, fullname: 'TSH fullname', alias: 'TSH', catalog: 'MAB-0162', incub: '60', ar: 'High PH'},
//    {id: 2, fullname: 'P57Kip2 fullname', alias: 'P57Kip2', catalog: 'MAB-0317', incub: '60', ar: 'High PH'},
//    {id: 3, fullname: 'Something Gold', alias: 'HBsAg', catalog: 'MAB-0587', incub: '60', ar: 'High PH'},
//    {id: 4, fullname: 'Actin', alias: 'Actin', catalog: 'Kit-0032', incub: '60', ar: 'High PH'},
//    {id: 5, fullname: 'Cytokine 5', alias: 'CK5', catalog: 'RMA-0612', incub: '60', ar: 'High PH'}
//]
const columns: GridColDef[] = [
    {field: 'id', headerName: 'ID', width: 70},
    {field: 'fullname', headerName: 'Full name', width: 250 },
    {field: 'alias', headerName: 'Alias', width: 250},
    {field: 'catalog', headerName: 'Catalog', width: 200},
    //{field: 'incub', headerName: 'Incubation', type: 'number', width: 90},
    {field: 'ar', headerName: 'AR', width: 130}
];

interface PAInformation {
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

class PA extends Component {
    state = { PAList: [] };
    componentDidMount() {
        axios.get<PAInformation[]>('api/pa/')
        .then((res) => {
            const PAList = res.data.map((obj, index)=> ({...obj, id: index}));
            this.setState({PAList});
        })
        .catch((err) => { console.log(err); });
    }
    render() {
        return(
        <div style={{height: 800, width: '100%'}}>
            <DataGrid rows={this.state.PAList} columns={columns} pageSize={25} checkboxSelection/>;
        </div>
        );
    }
}

export default PA;