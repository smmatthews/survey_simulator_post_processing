import pandas as pd
import numpy as np

__all__=['PPTranslateMagnitude']

def PPTranslateMagnitude(oif_output, survey_db, colors,
                         oifFieldIDName='FieldID', surveyFieldIDName='observationId',
                         surveyFilterName='filter',
                         oifObjIDName='ObjID', colorsObjIDName='ObjID',
                         oif_filter='V'
                         ):
    """
    Uses filter and color information from survey and color tables
    to translate V band magnitude to appropriate sdss filter magnitude.

    Input
    -----
    oif_output   ...   pandas table containing output of objectsInField simulator
    survey_db    ...   pandas table containing field conditions for each observation
    colors       ...   pandas table containing color difference between V band
                       appropriate filter bands for each object.

    Returns
    -------
    MaginFil     ...   pandas series containing translated magnitudes
    """

    df = pd.merge(
        oif_output[[oifObjIDName, oifFieldIDName]],
        survey_db[[surveyFieldIDName, surveyFilterName]],
        left_on=oifFieldIDName,
        right_on=surveyFieldIDName,
        how="left"
    ).drop(columns=[surveyFieldIDName])

    df = pd.merge(
        df,
        colors,
        left_on=oifObjIDName,
        right_on=colorsObjIDName,
        how="left"
    )

    df['filter diff name'] = oif_filter + '-' + df[surveyFilterName]
    idx, cols = pd.factorize(df['filter diff name'])

    filterDiff = df.reindex(cols, axis=1).to_numpy()[np.arange(len(df)), idx]

    return (oif_output[oif_filter] - filterDiff)
