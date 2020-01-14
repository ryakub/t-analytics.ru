import requests, json, time, pprint
import pandas as pd
import numpy as np
from yaml import load


class vk:
    def __init__(self, file_path):
        with open(file_path, 'r') as f:
            data = load(f)
        self.__access_token = data['vkontakte']['user_token']
        self.__client_id = data['vkontakte']['client_id']
        self.__client_secret = data['vkontakte']['client_secret']
        self.__redirect_uri = data['vkontakte']['redirect_uri']
        self.__v = data['vkontakte']['v']
        self.__display = data['vkontakte']['display']
        self.__method_url = data['vkontakte']['method_url']
        self.__scopes = data['vkontakte']['scopes']
    def __getProfileInfo(self):
        params = {'access_token': self.__access_token, 'v': self.__v}
        ProfileInfo = self.__Request('users.get', requestType = 'get')[0]
        return ProfileInfo['first_name'], ProfileInfo['last_name'], ProfileInfo['id']
    def __Slice(self, slice_ids, limit = 100, slice_list = []):
        count = len(slice_ids)
        if count > limit:
            slice_list.append(slice_ids[:limit])
            return self.__Slice(slice_ids[limit:], limit, slice_list = slice_list)
        else:
            slice_list.append(slice_ids)
            return slice_list
        return result
    def __Request(self, method, requestType = 'get', **kwargs):
        if "access_token" not in kwargs:
            params = {'access_token': self.__access_token, 'v': self.__v}
            for key, value in kwargs.items():
                params[key] = value
        else:
            params = kwargs
        if requestType == 'get':
            data = requests.get(self.__method_url + method, params = params).json()
        else:
            data = requests.post(self.__method_url + method, params = params).json()
        return self.__getErrors(data, method, params, requestType, i = 0)
    def __getErrors(self, response, method, params, requestType, i = 0):
        if "error" in response:
            time.sleep(7)
            if (response['error']['error_code'] not in [100, 9]) or (i > 5):
                raise Exception(response['error'])
            else:
                data = self.__Request(method, requestType, **params)
                i += 1
                return self.__getErrors(data, method, params, requestType)
        elif 'response' in response:
            return response['response']
        else:
            raise Exception("Это что-то новое")
    def getAccounts(self):
        Accounts = self.__Request('ads.getAccounts', requestType = 'get')
        Accounts = pd.DataFrame(Accounts)
        name, surname, user_id = self.__getProfileInfo()
        Accounts['user_id'] = user_id
        Accounts['user'] = name + " " + surname
        return Accounts
    def getClients(self, Accounts):
        all_clients = []
        for account_id in Accounts:
            clients = self.__Request('ads.getClients', requestType = 'get', account_id=account_id)
            for client in clients:
                client['account_id'] = account_id
                all_clients.append(client)
            time.sleep(2)
        all_clients_df = pd.DataFrame(all_clients)
        all_clients_df = df.rename(columns={'id': 'client_id', 'all_limit': 'client_all_limit', 'day_limit': 'client_day_limit',
                                    'name': 'client_name'})
        return all_clients_df
    def getCampaigns(self, account_id, client_id):
        Campaigns = self.__Request('ads.getCampaigns', requestType = 'get', account_id=account_id, include_deleted=1, client_id=client_id)
        Campaigns_df = pd.DataFrame(Campaigns)
        rename_columns = {}
        for column in Campaigns_df.columns:
            rename_columns[column] = "campaign_"+column
        Campaigns_df = Campaigns_df.rename(columns=rename_columns)
        Campaigns_df['client_id'] = client_id
        return Campaigns_df
    def getAds(self, account_id, client_id, campaign_ids):
        campaign_ids = self.__Slice(campaign_ids, slice_list = [])
        ads_list = []
        for campaign_ids_list in campaign_ids:
            campaign_ids_string = ",".join([str(x) for x in campaign_ids_list])
            Ads = self.__Request('ads.getAds', requestType = 'get', account_id=account_id, campaign_ids=f"[{campaign_ids_string}]", client_id=client_id)
            for ad in Ads:
                ads_list.append(ad)
            time.sleep(2)
        Ads_df = pd.DataFrame(ads_list)
        Ads_df['client_id'] = client_id
        Ads_df['account_id'] = account_id
        del(Ads_df['weekly_schedule_hours'], Ads_df['weekly_schedule_use_holidays'])
        return Ads_df
    def getGroups(self):
        Groups = self.__Request('groups.get', requestType = 'get', extended=1)
        params = {'access_token': self.__access_token, 'v': self.__v, "extended": 1}
        Groups_df = pd.DataFrame(Groups['items'])
        return Groups_df
    def getDayStats(self, account_id, ids_type, list_of_ids, date_from, date_to, limit = 2000):
        DayStat_list = []
        ids_list = self.__Slice(list_of_ids, limit, slice_list = [])
        for ids_stat_list in ids_list:
            ids_stat_string = ",".join([str(x) for x in ids_stat_list])
            DayStats = self.__Request('ads.getStatistics', requestType = 'get', account_id=account_id, ids_type=ids_type, ids=ids_stat_string, period="day", date_from=date_from, date_to=date_to)
            for DayStat in DayStats:
                for stat in DayStat['stats']:
                    DayStat_list.append(stat)
            time.sleep(2)
        DayStat_df = pd.DataFrame(DayStat_list).fillna(0)
        return DayStat_df
    def getPostsReach(self, account_id, PostReach_list_ids, limit = 100):
        PostsReach = []
        PostReach_list = self.__Slice(PostReach_list_ids, limit, slice_list = [])
        for PostReach_id_list in PostReach_list:
            PostReach_ids_string = ",".join([str(x) for x in PostReach_id_list])
            PostReachResponse = self.__Request('ads.getPostsReach', requestType = 'get', account_id=account_id, ids_type="ad", ids=PostReach_ids_string)
            for PostReach_stat in PostReachResponse:
                PostsReach.append(PostReach_stat)
            time.sleep(2)
        PostsReach_df = pd.DataFrame(PostsReach).fillna(0)
        return PostsReach_df
    # TODO: Доделать лбработку результатов в getDemographics
    def getDemographics(self, account_id, Demographics_list_ids, date_from, date_to, limit = 2000):
        Demographics = []
        Demographics_list = self.__Slice(Demographics_list_ids, limit, slice_list = [])
        for Demographics_id_list in Demographics_list:
            Demographics_ids_string = ",".join([str(x) for x in Demographics_id_list])
            DemographicsResponse = self.__Request('ads.getDemographics', requestType = 'get', account_id=account_id, ids_type="ad", ids=Demographics_ids_string, period="day", date_from=date_from, date_to=date_to)
#             for Demographics_stat in PostReachResponse:
#                 Demographics.append(Demographics_stat)
#             time.sleep(2)
#         Demographics_df = pd.DataFrame(Demographics).fillna(0)
            Demographics.append(DemographicsResponse)
        return Demographics
    def getAdsLayout(self, account_id, client_id, Ads_list_ids, limit = 2000):
        AdsLayout = []
        AdsLayout_list = self.__Slice(Ads_list_ids, limit, slice_list = [])
        for AdsLayout_id_list in AdsLayout_list:
            AdsLayout_ids_string = ",".join([str(x) for x in AdsLayout_id_list])
            AdsLayoutResponse = self.__Request('ads.getAdsLayout', requestType = 'get', account_id=account_id, client_id=client_id, ad_ids=f"[{AdsLayout_ids_string}]", include_deleted=1)
            for AdsLayout_stat in AdsLayoutResponse:
                AdsLayout.append(AdsLayout_stat)
            time.sleep(2)
        AdsLayout_df = pd.DataFrame(AdsLayout).fillna(0)
        return AdsLayout_df